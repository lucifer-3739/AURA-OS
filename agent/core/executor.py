from typing import Dict, Any, Optional
from agent.tools import registry
from agent.security import permission_manager, audit_logger, PermissionStatus, RiskLevel
from agent.core.verifier import verifier

class StepExecutionResult:
    def __init__(
        self,
        success: bool,
        status: str,  # EXECUTED, WAITING_FOR_PERMISSION, REJECTED, FAILED
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        permission_status: PermissionStatus = PermissionStatus.AUTO_APPROVED,
        risk_level: RiskLevel = RiskLevel.SAFE
    ):
        self.success = success
        self.status = status
        self.result = result or {}
        self.error = error
        self.permission_status = permission_status
        self.risk_level = risk_level

class TaskExecutor:
    async def execute_step(
        self,
        step: Dict[str, Any],
        task_id: str,
        user_confirmed: Optional[bool] = None
    ) -> StepExecutionResult:
        tool_name = step.get("tool_name")
        arguments = step.get("arguments", {})

        tool = registry.get_tool(tool_name)
        if not tool:
            return StepExecutionResult(
                success=False,
                status="FAILED",
                error=f"Registered tool '{tool_name}' not found"
            )

        risk_level = tool.metadata.risk_level
        perm_status = permission_manager.evaluate(risk_level, user_confirmed)

        if perm_status == PermissionStatus.PENDING:
            return StepExecutionResult(
                success=False,
                status="WAITING_FOR_PERMISSION",
                risk_level=risk_level,
                permission_status=perm_status
            )

        if perm_status == PermissionStatus.USER_REJECTED:
            await audit_logger.log_tool_execution(
                tool_name=tool_name,
                arguments=arguments,
                result={"error": "User rejected permission"},
                risk_level=risk_level,
                permission_status=perm_status,
                task_id=task_id
            )
            return StepExecutionResult(
                success=False,
                status="REJECTED",
                error="Action rejected by user",
                permission_status=perm_status,
                risk_level=risk_level
            )

        # Execute tool
        try:
            exec_res = await tool.execute(**arguments)
        except Exception as e:
            exec_res = {"success": False, "error": str(e)}

        # Verify step
        verified, ver_msg = await verifier.verify_step(tool_name, arguments, exec_res)
        if not verified:
            exec_res["success"] = False
            exec_res["verification_error"] = ver_msg

        # Audit log
        await audit_logger.log_tool_execution(
            tool_name=tool_name,
            arguments=arguments,
            result=exec_res,
            risk_level=risk_level,
            permission_status=perm_status,
            task_id=task_id
        )

        status_str = "EXECUTED" if verified else "FAILED"
        return StepExecutionResult(
            success=verified,
            status=status_str,
            result=exec_res,
            error=exec_res.get("error") or exec_res.get("verification_error"),
            permission_status=perm_status,
            risk_level=risk_level
        )

executor = TaskExecutor()
