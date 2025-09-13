import logging
from pathlib import Path

import chromadb
from fastmcp.tools import Tool as FastMCPTool
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

from mcp_llamaindex.servers.base import BaseServer


class DirectoryRagServer(BaseServer):
    """A server for RAG."""
    server_name: str = "DirectoryRagServer"

    def get_tools(self) -> list[FastMCPTool]:
        """Get the tools for the server."""
        return [
            FastMCPTool.from_function(fn=self.query),
        ]

    def _load_documents(self, data_dir: str) -> list:
        """
        Loads all markdown documents from the specified directory.
        """
        p = Path(data_dir)
        if not p.exists():
            raise FileNotFoundError(f"Data directory '{data_dir}' not found. Please create it and add markdown files.")

        reader = SimpleDirectoryReader(input_dir=data_dir)
        documents = reader.load_data()

        logging.debug(f"Loaded {len(documents)} documents from '{data_dir}'.")
        return documents


    def _setup_llm_and_embeddings(self):
        """
        Configures LlamaIndex to use LLM and embedding model.
        """
        # Optional: Configure local LLM (e.g., Llama 3 via Ollama)
        Settings.llm = LMStudio(
            model_name="openai/gpt-oss-20b",
            base_url="http://localhost:1234/v1",
            request_timeout=120.0,  # Increased timeout for potentially longer generations
            context_window=4096  # Important for memory management with local LLMs
        )

        # Configure local embedding model (e.g., BGE Large)
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-large-en-v1.5",
        )

        # The same embedding model must be used for both indexing and querying
        logging.debug("LLM and embedding model configured.")


    def _teardown_llm_and_embeddings(self):
        """
        Resets LlamaIndex global settings to their default values.
        """
        # Reset LLM to default (usually None or the default LlamaIndex provider)
        Settings.llm = None

        # Reset embedding model to default
        Settings.embed_model = None

        logging.debug("LLM and embedding model settings have been reset.")


    def _get_or_create_index(self, documents: list, persist_dir: str):
        """
        Loads an existing LlamaIndex from disk or creates a new one if it doesn't exist.
        Persists the index using ChromaDB.
        """
        persist_dir = Path(persist_dir)
        if not persist_dir.exists():
            persist_dir.mkdir(parents=True)

        # Initialize ChromaDB client, collection and vector store
        db = chromadb.PersistentClient(path=persist_dir)
        chroma_collection = db.get_or_create_collection("markdown_rag_collection")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

        try:
            # Attempt to load existing index from storage context
            # Note: For ChromaDB, `load_index_from_storage` needs the vector_store in storage_context
            storage_context = StorageContext.from_defaults(vector_store=vector_store, persist_dir=str(persist_dir))
            index = load_index_from_storage(storage_context=storage_context)
            logging.debug("Loaded existing LlamaIndex from disk using ChromaDB.")
        except Exception as e:  # Catching a broad exception for demonstration, be more specific in production
            logging.warning(f"Could not load existing index ({e}). Creating a new LlamaIndex...")
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
            )
            # Persist the newly created index
            index.storage_context.persist(persist_dir=persist_dir)
            logging.debug("New LlamaIndex created and persisted to disk.")

        return index


    def _get_rag_query_engine(self, index: VectorStoreIndex, top_k: int = 3) -> RetrieverQueryEngine:
        """
        Creates and returns a LlamaIndex query engine for RAG.
        """
        retriever = VectorIndexRetriever(index=index, similarity_top_k=top_k)
        response_synthesizer = CompactAndRefine()

        query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer
        )
        logging.debug("LlamaIndex query engine created.")
        return query_engine