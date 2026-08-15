from typing import Dict, Any, Tuple
from agent.tools import registry

class ActionVerifier:
    async def verify_step(self, tool_name: str, arguments: Dict[str, Any], result: Dict[str, Any]) -> Tuple[bool, str]:
        tool = registry.get_tool(tool_name)
        if not tool:
            return False, f"Tool '{tool_name}' not registered in tool system."

        # Check basic execution status
        if not result.get("success", False):
            err = result.get("error", "Unknown tool execution failure")
            return False, f"Tool execution failed: {err}"

        # Run custom verification routine if present
        is_valid = await tool.verify(result, **arguments)
        if not is_valid:
            return False, f"Action verification failed for tool '{tool_name}' with parameters {arguments}."

        return True, "Step verified successfully."

verifier = ActionVerifier()
