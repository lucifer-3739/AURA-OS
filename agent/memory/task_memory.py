import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from agent.database import db

class TaskMemory:
    async def create_task(self, task_id: str, user_request: str, plan: List[Dict[str, Any]], status: str = "PLANNING"):
        query = """
            INSERT INTO tasks (task_id, user_request, status, plan, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        now = datetime.now(timezone.utc).isoformat()
        await db.execute_write(query, (task_id, user_request, status, json.dumps(plan), now, now))

    async def update_task_status(self, task_id: str, status: str, plan: Optional[List[Dict[str, Any]]] = None):
        now = datetime.now(timezone.utc).isoformat()
        if plan is not None:
            query = "UPDATE tasks SET status = ?, plan = ?, updated_at = ? WHERE task_id = ?"
            await db.execute_write(query, (status, json.dumps(plan), now, task_id))
        else:
            query = "UPDATE tasks SET status = ?, updated_at = ? WHERE task_id = ?"
            await db.execute_write(query, (status, now, task_id))

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM tasks WHERE task_id = ?"
        row = await db.fetch_one(query, (task_id,))
        if not row:
            return None
        task = dict(row)
        task["plan"] = json.loads(task["plan"])
        return task

    async def list_tasks(self, limit: int = 50) -> List[Dict[str, Any]]:
        query = "SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?"
        rows = await db.fetch_all(query, (limit,))
        tasks = []
        for r in rows:
            t = dict(r)
            t["plan"] = json.loads(t["plan"])
            tasks.append(t)
        return tasks

task_memory = TaskMemory()
