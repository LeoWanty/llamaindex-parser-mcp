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

## Configuration

The application's configuration is managed using Pydantic and environment files. The environment can be set to either `dev` or `prod`.

To select an environment, set the `ENV_TYPE` environment variable:

```bash
export ENV_TYPE=prod
```

The application will then load its settings from the corresponding `.env` file (`.prod.env` in this case).

The following environment variables are available:

-   `LOG_LEVEL`: The logging level (e.g., `DEBUG`, `INFO`).
-   `DATABASE_URL`: The connection string for the database.

Example `.dev.env` file:

```
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///./test.db
ENV_TYPE=dev
```

Example `.prod.env` file:

```
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:password@prod-db:5432/mydatabase
ENV_TYPE=prod
```
**Note:** The `.env` files are not committed to version control. You should create your own `.dev.env` and `.prod.env` files based on the `.example.env` file.

## Contributing

We welcome contributions to this project! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) to learn how you can contribute.