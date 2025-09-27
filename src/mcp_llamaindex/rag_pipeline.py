from functools import lru_cache
from pathlib import Path
from typing import Any

from fastmcp import FastMCP, Context
from fastmcp.utilities.logging import get_logger
from pydantic import Field, BaseModel

import chromadb
from fastmcp.tools import Tool as FastMCPTool
from fastmcp.resources import Resource as FastMCPResource
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.lmstudio import LMStudio
from llama_index.core import (
    SimpleDirectoryReader,
    Settings,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.response_synthesizers import CompactAndRefine
from llama_index.vector_stores.chroma import ChromaVectorStore

from mcp_llamaindex.config import settings
from mcp_llamaindex.servers.base import BaseServer

logger = get_logger(__name__)

# Optional: Configure local LLM (e.g., Llama 3 via Ollama)
Settings.llm = LMStudio(
    model_name=settings.summary_model,
    base_url="http://localhost:1234/v1",
    request_timeout=120.0,  # Increased timeout for potentially longer generations
    context_window=4096  # Important for memory management with local LLMs
)

# Configure local embedding model (e.g., BGE Large)
Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-large-en-v1.5",
)

# The same embedding model must be used for both indexing and querying
logger.debug("LLM and embedding model configured.")


class RagConfig(BaseModel):
    """Configuration for RAG."""
    # vector_store
    persist_dir: str | Path = settings.STATIC_DIR / "vector_store"
    data_dir: str | Path = settings.STATIC_DIR / "md_documents"

    # retrieval
    top_k: int = 3


class DirectoryRagServer(BaseServer):
    """A server for RAG."""
    # FastMCP server
    server_name: str = "Directory Rag Server"
    server_instructions: str = """
This server provides Retrieval-Augmented Generation (RAG) capabilities over your local Markdown documentation.
You can ask questions about your documents, and the server will retrieve relevant information and generate an answer.
"""
    server_dependencies: list[str] = ["llama-index", "llama-index-llms-ollama", "llama-index-vector-stores-chroma", "chromadb"]

    # RAG pipeline
    rag_config: RagConfig = Field(default_factory=RagConfig)

    @property
    def documents(self) -> list:
        return self._load_documents(self.rag_config.data_dir)

    @property
    def index(self) -> VectorStoreIndex:
        return self._get_or_create_index()

    @property
    def rag_query_engine(self) -> RetrieverQueryEngine:
        return self._instantiate_rag_query_engine(self.index, self.rag_config.top_k)

    def get_tools(self) -> list[FastMCPTool]:
        """Get the tools for the server."""
        return [
            FastMCPTool.from_function(fn=self.query_markdown_docs),
            FastMCPTool.from_function(fn=self.query_markdown_docs_bis),
            FastMCPTool.from_function(fn=self.get_indexed_files),
        ]

    def get_resources(self) -> list[FastMCPResource]:
        """Get the resources for the server."""
        return [
            FastMCPResource.from_function(fn=self.list_markdown_files, uri="data://list-markdown-files"),
        ]

    def as_server(self) -> FastMCP:
        """Instantiate a FastMCP server."""
        mcp: FastMCP[Any] = FastMCP[Any](
            name=self.server_name,
            instructions=self.server_instructions,
            dependencies=self.server_dependencies,
        )

        [mcp.add_tool(tool=tool) for tool in self.get_tools()]
        [mcp.add_resource(resource=resource) for resource in self.get_resources()]
        return mcp

    def query_markdown_docs(self, query: str) -> str:
        """
        Answers questions by performing Retrieval-Augmented Generation (RAG)
        over the local Markdown documentation. Provide a clear and concise
        question related to the documents.

        Args:
            query (str): The question to ask about the Markdown documents.

        Returns:
            str: The generated answer based on the retrieved context.
        """
        if self.rag_query_engine is None:
            return "Error: RAG pipeline not initialized. Please ensure Markdown files are present, Ollama is running, and the server started correctly."

        response = self.rag_query_engine.query(query)
        return str(response)

    async def query_markdown_docs_bis(self, query: str, ctx: Context) -> str:
        """
        Answers questions by performing Retrieval-Augmented Generation (RAG)
        over the local Markdown documentation. Provide a clear and concise
        question related to the documents.

        SUMMARIZING IS DONE THROUGH LLM SAMPLING, NOT BY THE SERVER ITSELF.

        Args:
            ctx: FastMCP context.
            query (str): The question to ask about the Markdown documents.

        Returns:
            str: The generated answer based on the retrieved context.
        """
        if self.rag_query_engine is None:
            return "Error: RAG pipeline not initialized. Please ensure Markdown files are present, Ollama is running, and the server started correctly."

        retrieved_docs = self.rag_query_engine.retrieve(query)
        question_prompt = f"Query: {query}"
        system_prompt = "You're an assistant that summarizes documents to answer a user query."
        prompt = "\n\n___\n\n".join(
            [question_prompt] + [f"Document {i}:\n"+ node.get_content() for i, node in enumerate(retrieved_docs)]
        )
        response = await ctx.sample(prompt, system_prompt=system_prompt, max_tokens=10000)
        return response.text

    def query_and_get_nodes(self, query: str) -> tuple[str, list[dict]]:
        """
        Answers questions and returns the retrieved source nodes.

        Args:
            query (str): The question to ask about the Markdown documents.

        Returns:
            tuple[str, list[dict]]: A tuple containing the generated answer
                                     and a list of retrieved source nodes as dictionaries.
        """
        if self.rag_query_engine is None:
            return "Error: RAG pipeline not initialized.", []

        response = self.rag_query_engine.query(query)
        nodes = [
            {
                "node": {
                    "text": n.node.get_content(),
                    "metadata": n.node.metadata,
                },
                "score": n.score,
            }
            for n in response.source_nodes
        ]
        return str(response), nodes

    def get_indexed_files(self) -> list[str]:
        """
        Lists the names of all files that have been indexed in the RAG knowledge base.
        """
        if not self.index:
            raise AttributeError("Index not found or empty. Please ensure Markdown files are present, Ollama is running, and the server started correctly.")

        chroma_collection = self.index.vector_store._collection
        metadatas = chroma_collection.get(include=["metadatas"])
        file_paths = {m.get("file_name") for m in metadatas['metadatas']}
        # Filter out None values in case some documents don't have a file_name
        return sorted([fp for fp in file_paths if fp])

    def list_markdown_files(self) -> list[str]:
        """
        Lists the names of all Markdown files available in the RAG knowledge base.
        """
        if not self.rag_config.data_dir.exists():
            return ["No directory found."]

        markdown_files = [str(f.name) for f in self.rag_config.data_dir.iterdir() if f.is_file() and f.suffix == ".md"]
        return markdown_files

    @staticmethod
    @lru_cache(maxsize=1)
    def _load_documents(data_dir: str | Path) -> list:
        """
        Loads all Markdown documents from the specified directory.
        """
        p = Path(data_dir)
        if not p.exists():
            raise FileNotFoundError(f"Data directory '{data_dir}' not found. Please create it and add Markdown files.")

        reader = SimpleDirectoryReader(input_dir=data_dir)
        documents = reader.load_data()

        logger.debug(f"Loaded {len(documents)} documents from '{data_dir}'.")
        return documents

    @lru_cache(maxsize=1)
    def _get_or_create_index(self):
        """
        Loads an existing LlamaIndex from the disk or creates a new one if it doesn't exist.
        Persists the index using ChromaDB.
        """
        persist_dir = Path(self.rag_config.persist_dir)
        if not persist_dir.exists():
            persist_dir.mkdir(parents=True)

        # Initialize ChromaDB client, collection and vector store
        db = chromadb.PersistentClient(path=persist_dir)
        chroma_collection = db.get_or_create_collection("markdown_rag_collection")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

        try:
            # Attempt to load an existing index from storage context
            # Note: For ChromaDB, `load_index_from_storage` needs the vector_store in storage_context
            storage_context = StorageContext.from_defaults(vector_store=vector_store, persist_dir=str(persist_dir))
            index = load_index_from_storage(storage_context=storage_context)
            logger.debug("Loaded existing LlamaIndex from disk using ChromaDB.")
        except Exception as e:  # TODO : Catching a broad exception for demonstration, be more specific in production
            logger.warning(f"Could not load existing index ({e}). Creating a new LlamaIndex...")
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            index = VectorStoreIndex.from_documents(
                self.documents,
                storage_context=storage_context,
            )
            # Persist the newly created index
            index.storage_context.persist(persist_dir=persist_dir)
            logger.debug("New LlamaIndex created and persisted to disk.")

        return index

    @staticmethod
    @lru_cache(maxsize=1)
    def _instantiate_rag_query_engine(index: VectorStoreIndex, top_k: int = 3) -> RetrieverQueryEngine:
        """
        Creates and returns a LlamaIndex query engine for RAG.
        """
        retriever = VectorIndexRetriever(index=index, similarity_top_k=top_k)
        response_synthesizer = CompactAndRefine()

        query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer
        )
        logger.debug("LlamaIndex query engine created.")
        return query_engine