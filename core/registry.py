from typing import Callable, Dict, Any


ToolFunc = Callable[[Dict[str, Any]], Any]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, ToolFunc] = {}

    def register(self, name: str):
        """Decorator to register a tool by name."""
        def decorator(func: ToolFunc) -> ToolFunc:
            self._tools[name] = func
            return func
        return decorator

    def get(self, name: str) -> ToolFunc:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found")
        return self._tools[name]

    def list_tools(self) -> Dict[str, str]:
        return {name: func.__doc__ or "" for name, func in self._tools.items()}


tool_registry = ToolRegistry()
