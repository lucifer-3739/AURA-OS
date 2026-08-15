import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from agent.database import db
from agent.security.permissions import RiskLevel, PermissionStatus

logger = logging.getLogger("AURA_OS.Audit")

class AuditLogger:
    @staticmethod
    async def log_tool_execution(
        tool_name: str,
        arguments: Dict[str, Any],
        result: Any,
        risk_level: RiskLevel,
        permission_status: PermissionStatus,
        task_id: Optional[str] = None
    ) -> int:
        args_str = json.dumps(arguments, default=str)
        res_str = json.dumps(result, default=str)
        
        # Log to Python standard structured logger
        logger.info(
            f"[AUDIT] task_id={task_id} tool={tool_name} risk={risk_level.value} "
            f"permission={permission_status.value} args={args_str}"
        )

        # Log into SQLite DB table
        query = """
            INSERT INTO audit_log (task_id, timestamp, tool_name, arguments, result, risk_level, permission_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        row_id = await db.execute_write(
            query,
            (task_id, datetime.now(timezone.utc).isoformat(), tool_name, args_str, res_str, risk_level.value, permission_status.value)
        )
        return row_id

audit_logger = AuditLogger()
