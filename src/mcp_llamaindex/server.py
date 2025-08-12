import json
from mcp.server.fastmcp import FastMCP
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import MarkdownNodeParser

# Initialize FastMCP server
mcp = FastMCP("llamaindex_loader")

@mcp.tool()
async def load_markdown_data(path: str) -> str:
    """
    Load and parse markdown data from a given path.

    Args:
        path: The path to the directory containing the markdown files.

    Returns:
        A JSON string representing the parsed markdown nodes.
    """
    try:
        documents = SimpleDirectoryReader(path).load_data()
        parser = MarkdownNodeParser()
        nodes = parser.get_nodes_from_documents(documents)
        nodes_as_dicts = [node.to_dict() for node in nodes]
        return json.dumps(nodes_as_dicts, indent=2)
    except Exception as e:
        return f"Error loading and parsing data: {e}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
