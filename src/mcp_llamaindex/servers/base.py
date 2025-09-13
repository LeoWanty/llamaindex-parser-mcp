from abc import ABC, abstractmethod
from typing import Any, ClassVar

from fastmcp import FastMCP
from fastmcp.tools import Tool as FastMCPTool
from pydantic import BaseModel, ConfigDict


class BaseServer(BaseModel, ABC):
    """A base server for all servers."""
    server_name: str

    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

    @abstractmethod
    def get_tools(self) -> list[FastMCPTool]: ...

    @abstractmethod
    def as_server(self) -> FastMCP[Any]:
        """Convert the server to a FastMCP server."""
        ...