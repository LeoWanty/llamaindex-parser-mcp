from contextlib import asynccontextmanager

from fastmcp import FastMCP

from mcp_llamaindex.config import STATIC_DIR
from mcp_llamaindex.rag_pipeline import (
    load_documents,
    setup_llm_and_embeddings,
    get_or_create_index,
    get_rag_query_engine,
    teardown_llm_and_embeddings
)

# Global variable to hold the initialized RAG query engine
rag_query_engine = None


@asynccontextmanager
async def app_lifespan(app):
    """
    Initializes the LlamaIndex RAG pipeline when the MCP server starts.
    """
    print("Starting up: Initializing RAG pipeline...")
    try:
        setup_llm_and_embeddings()
        documents = load_documents(STATIC_DIR / "md_documents")
        if not documents:
            print("No markdown documents found. RAG will not function.")

        index = get_or_create_index(documents, persist_dir = STATIC_DIR / "vector_store")
        global rag_query_engine
        rag_query_engine = get_rag_query_engine(index)
        print("RAG pipeline initialized successfully.")
    except Exception as e:
        print(f"Error initializing RAG pipeline: {e}")
        raise (e)
        # Depending on severity, you might want to prevent server from starting

    yield

    print("Shutting down: RAG pipeline cleanup...")
    teardown_llm_and_embeddings()
    del rag_query_engine


# Initialize FastMCP server
mcp = FastMCP(
    name="Local Markdown RAG Server",
    instructions="This server provides Retrieval-Augmented Generation (RAG) capabilities over your local markdown documentation."
                 "You can ask questions about your documents, and the server will retrieve relevant information and generate an answer.",
    dependencies=["llama-index", "llama-index-llms-ollama", "llama-index-vector-stores-chroma", "chromadb"],
    lifespan=app_lifespan,
)


@mcp.tool()
def query_markdown_docs(query: str) -> str:
    """
    Answers questions by performing Retrieval-Augmented Generation (RAG)
    over the local markdown documentation. Provide a clear and concise
    question related to the documents.

    Args:
        query (str): The question to ask about the markdown documents.

    Returns:
        str: The generated answer based on the retrieved context.
    """
    if rag_query_engine is None:
        return "Error: RAG pipeline not initialized. Please ensure markdown files are present, Ollama is running, and the server started correctly."

    # return f"Received query for RAG: '{query}'"
    response = rag_query_engine.query(query)
    return str(response)


@mcp.resource("data://markdown-files")
def list_markdown_files() -> list[str]:
    """
    Lists the names of all markdown files available in the RAG knowledge base.
    """
    data_dir = STATIC_DIR / "md_documents"
    if not data_dir.exists():
        return ["No directory found."]

    markdown_files = [str(f.name) for f in data_dir.iterdir() if f.is_file() and f.suffix == ".md"]
    print(f"Listing {len(markdown_files)} markdown files.")
    return markdown_files

if __name__ == "__main__":
    mcp.run(transport='stdio')
