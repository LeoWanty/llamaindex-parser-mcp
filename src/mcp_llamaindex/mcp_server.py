import logging

from mcp_llamaindex.rag_pipeline import DirectoryRagServer

# Initialize FastMCP server
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s\t%(message)s",
    datefmt="%m/%d/%y %H:%M:%S",
)
mcp = DirectoryRagServer().as_server()

if __name__ == "__main__":
    mcp.run(transport='stdio')
