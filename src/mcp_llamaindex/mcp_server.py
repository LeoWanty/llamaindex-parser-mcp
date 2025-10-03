import logging

from mcp_llamaindex.dir_rag_server import DirectoryRagServer

# Initialize FastMCP server
mcp = DirectoryRagServer().as_server()

if __name__ == "__main__":
    logging.info(">>> Starting MCP server")
    mcp.run(transport="stdio")
