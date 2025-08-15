import json
from pathlib import Path

from fastmcp import FastMCP
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import MarkdownNodeParser

# Initialize FastMCP server
mcp = FastMCP("llamaindex_loader")

@mcp.tool()
async def load_markdown_data(path: str | Path | list[str] | list[Path]) -> str:
    """
    Load and parse markdown data from a given path.

    Args:
        path: The path to the directory containing the markdown files,
          OR path to a single markdown file,
          OR list of paths to markdown files.

    Returns:
        A JSON string representing the parsed markdown nodes.
    """
    path = Path(path)
    try:
        if Path(path).is_dir():
            documents = SimpleDirectoryReader(path)
        else:
            if not isinstance(path, list):
                path = [path]
            documents = SimpleDirectoryReader(input_files=path)

        documents=documents.load_data()
        parser = MarkdownNodeParser()
        nodes = parser.get_nodes_from_documents(documents)
        nodes_as_dicts = [node.to_dict() for node in nodes]
        return json.dumps(nodes_as_dicts, indent=2)
    except Exception as e:
        return f"Error loading and parsing data: {e}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
