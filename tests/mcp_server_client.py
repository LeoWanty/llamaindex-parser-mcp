import logging

from fastmcp.client import Client

from mcp_llamaindex.mcp_server import mcp
from tests.local_client import sampling_handler


client = Client(
    mcp,
    sampling_handler=sampling_handler,
)


async def main():
    async with client:
        # Basic server interaction
        await client.ping()

        # # List available operations
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()
        logging.warning(tools)
        logging.warning(resources)
        logging.warning(prompts)

        sampling_result = await client.call_tool(
            "query_markdown_docs_bis", {"query": "What is ReACT"}
        )
        logging.warning(sampling_result)
        return sampling_result
