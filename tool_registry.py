from models import BaseTool
from typing import Any

class ToolRegistry:
    def __init__(self):
        self._tool_dict: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """
        Register a tool instance.
        Raises ValueError if a tool with the same id already exists.
        """
        if tool.identifier in self._tool_dict:
            raise ValueError(f"Tool with id '{tool.identifier}' is already registered.")

        self._tool_dict[tool.identifier] = tool

    def unregister(self, tool_identifier: str) -> None:
        """Remove a tool from registry and index."""
        if tool_identifier not in self._tool_dict:
            raise KeyError(f"Tool with id '{tool_identifier}' not found.")
        del self._tool_dict[tool_identifier]

    def get_tool(self, tool_identifier: str) -> BaseTool:
        """Retrieve a tool by its id."""
        if tool_identifier not in self._tool_dict:
            raise KeyError(f"Tool with id '{tool_identifier}' not found.")
        return self._tool_dict[tool_identifier]

    def list_tools(self) -> list[str]:
        """Return metadata for all registered tools"""
        return [tool.tool_info() for tool in self._tool_dict.values()]

    def has_tool(self, tool_id: str) -> bool:
        """Check if a tool is registered."""
        return tool_id in self._tool_dict