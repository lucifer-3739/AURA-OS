import json
from typing import Any, Optional, Dict
from datetime import datetime, timezone
from agent.database import db

class LongTermMemory:
    async def set_preference(self, key: str, value: Any):
        val_str = json.dumps(value) if not isinstance(value, str) else value
        query = """
            INSERT INTO memory_long_term (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
        """
        await db.execute_write(query, (key, val_str, datetime.now(timezone.utc).isoformat()))

    async def get_preference(self, key: str, default: Any = None) -> Any:
        query = "SELECT value FROM memory_long_term WHERE key = ?"
        row = await db.fetch_one(query, (key,))
        if not row:
            return default
        try:
            return json.loads(row["value"])
        except Exception:
            return row["value"]

    async def get_all(self) -> Dict[str, Any]:
        query = "SELECT key, value FROM memory_long_term"
        rows = await db.fetch_all(query)
        result = {}
        for r in rows:
            try:
                result[r["key"]] = json.loads(r["value"])
            except Exception:
                result[r["key"]] = r["value"]
        return result

long_term_memory = LongTermMemory()
