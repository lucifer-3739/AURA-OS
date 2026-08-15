import inspect
from typing import Callable, Dict, Any, Optional, List
from pydantic import BaseModel
from agent.security.permissions import RiskLevel

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    risk_level: RiskLevel
    required_permission: str

class Tool:
    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        risk_level: RiskLevel,
        required_permission: str,
        func: Callable,
        verify_func: Optional[Callable] = None
    ):
        self.metadata = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters,
            risk_level=risk_level,
            required_permission=required_permission
        )
        self.func = func
        self.verify_func = verify_func

    async def execute(self, **kwargs) -> Dict[str, Any]:
        if inspect.iscoroutinefunction(self.func):
            return await self.func(**kwargs)
        return self.func(**kwargs)

    async def verify(self, result: Dict[str, Any], **kwargs) -> bool:
        if self.verify_func is None:
            # Default verification checks if result success flag is True
            return result.get("success", False)
        if inspect.iscoroutinefunction(self.verify_func):
            return await self.verify_func(result, **kwargs)
        return self.verify_func(result, **kwargs)

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        risk_level: RiskLevel,
        required_permission: str = "default",
        verify_func: Optional[Callable] = None
    ):
        def decorator(func: Callable):
            tool = Tool(
                name=name,
                description=description,
                parameters=parameters,
                risk_level=risk_level,
                required_permission=required_permission,
                func=func,
                verify_func=verify_func
            )
            self._tools[name] = tool
            return func
        return decorator

    def get_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        return [tool.metadata.model_dump() for tool in self._tools.values()]

registry = ToolRegistry()
