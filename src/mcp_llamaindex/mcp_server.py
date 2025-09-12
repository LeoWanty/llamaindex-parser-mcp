import logging

from fastmcp import FastMCP

from mcp_llamaindex.config import STATIC_DIR
from mcp_llamaindex.rag_pipeline import (
    load_documents,
    setup_llm_and_embeddings,
    get_or_create_index,
    get_rag_query_engine,
)

# TODO : find a cleaner pattern to handle index and vector store init
# TODO : find a pattern to handle teardown with FastMCP
try:
    logging.info("Starting up: Initializing RAG pipeline...")
    setup_llm_and_embeddings()
    documents = load_documents(STATIC_DIR / "md_documents")
    if not documents:
        logging.warning("No markdown documents found. RAG will not function.")

    index = get_or_create_index(documents, persist_dir=STATIC_DIR / "vector_store")
    rag_query_engine = get_rag_query_engine(index)
    logging.info("RAG pipeline initialized successfully.")
except Exception as e:
    raise e


# Initialize FastMCP server
mcp = FastMCP(
    name="Local Markdown RAG Server",
    instructions="This server provides Retrieval-Augmented Generation (RAG) capabilities over your local markdown documentation."
                 "You can ask questions about your documents, and the server will retrieve relevant information and generate an answer.",
    dependencies=["llama-index", "llama-index-llms-ollama", "llama-index-vector-stores-chroma", "chromadb"],
)


@mcp.tool()
async def query_markdown_docs(query: str) -> str:
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
    return markdown_files

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s\t%(message)s",
        datefmt="%m/%d/%y %H:%M:%S",
    )
    mcp.run(transport='stdio')
