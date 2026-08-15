import os
import sys
from typing import Dict, Any, List
from agent.memory import short_term_memory, long_term_memory
from agent.tools import registry

class ContextBuilder:
    async def build_context(self, session_id: str, user_request: str) -> Dict[str, Any]:
        # 1. System state
        sys_info = {
            "os": sys.platform,
            "cwd": os.getcwd(),
        }

        # 2. Registered tools list
        tools_available = registry.list_tools()

        # 3. Short term conversation history
        history = await short_term_memory.get_history(session_id, limit=5)

        # 4. Long term user preferences
        preferences = await long_term_memory.get_all()

        return {
            "user_request": user_request,
            "system_info": sys_info,
            "tools": tools_available,
            "conversation_history": history,
            "user_preferences": preferences
        }

context_builder = ContextBuilder()
