# LlamaIndex Parser MCP Server

This project provides a server that exposes LlamaIndex's parsing capabilities through a simple interface. It is built using the `FastMCP` framework.

The server has a tool called `load_markdown_data` that can load and parse markdown files from a specified directory and return the parsed nodes as a JSON string.

## Installation

To install the project and its dependencies, run the following commands:

```bash
uv sync
pip install -e .
```

## Usage

To run the server, execute the following command from the root of the repository:

```bash
python src/mcp_llamaindex/server.py
```

The server will start and listen for requests on `stdio`.

## Dev mode

To run the server in dev mode:
```bash
fastmcp dev src/mcp_llamaindex/server.py
```

## Contributing

We welcome contributions to this project! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) to learn how you can contribute.