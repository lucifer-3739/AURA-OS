from typing import List, Dict, Any
from datetime import datetime, timezone
from agent.database import db

class ShortTermMemory:
    async def add_message(self, session_id: str, role: str, content: str) -> int:
        query = """
            INSERT INTO memory_short_term (session_id, role, content, timestamp)
            VALUES (?, ?, ?, ?)
        """
        return await db.execute_write(query, (session_id, role, content, datetime.now(timezone.utc).isoformat()))

    async def get_history(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        query = """
            SELECT role, content, timestamp FROM memory_short_term
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
        """
        rows = await db.fetch_all(query, (session_id, limit))
        return list(reversed(rows))

    async def clear_session(self, session_id: str):
        query = "DELETE FROM memory_short_term WHERE session_id = ?"
        await db.execute_write(query, (session_id,))

short_term_memory = ShortTermMemory()
