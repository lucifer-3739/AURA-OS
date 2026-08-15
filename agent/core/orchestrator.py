import uuid
import inspect
import asyncio
import logging
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from agent.memory import task_memory, short_term_memory
from agent.core.context import context_builder
from agent.core.planner import planner_provider
from agent.core.executor import executor
from agent.security import RiskLevel

logger = logging.getLogger("AURA_OS.Orchestrator")

class TaskState(str, Enum):
    IDLE = "IDLE"
    WAITING_FOR_WAKE_WORD = "WAITING_FOR_WAKE_WORD"
    WAKE_WORD_DETECTED = "WAKE_WORD_DETECTED"
    LISTENING = "LISTENING"
    PROCESSING_SPEECH = "PROCESSING_SPEECH"
    UNDERSTANDING = "UNDERSTANDING"
    PLANNING = "PLANNING"
    THINKING = "THINKING"
    WAITING_FOR_PERMISSION = "WAITING_FOR_PERMISSION"
    EXECUTING = "EXECUTING"
    OBSERVING = "OBSERVING"
    VERIFYING = "VERIFYING"
    SPEAKING = "SPEAKING"
    INTERRUPTED = "INTERRUPTED"
    RECOVERING = "RECOVERING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    ERROR = "ERROR"

class AgentOrchestrator:
    def __init__(self):
        self.current_state: TaskState = TaskState.IDLE
        self.current_task_id: Optional[str] = None
        self.current_plan: List[Dict[str, Any]] = []
        self.pending_step: Optional[Dict[str, Any]] = None
        self.pending_risk_level: Optional[RiskLevel] = None
        self.event_subscribers: List[Callable[[Dict[str, Any]], None]] = []

    def subscribe(self, callback: Callable[[Dict[str, Any]], None]):
        self.event_subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[Dict[str, Any]], None]):
        if callback in self.event_subscribers:
            self.event_subscribers.remove(callback)

    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        payload = {
            "event": event_type,
            "task_id": self.current_task_id,
            "state": self.current_state.value,
            "data": data
        }
        for cb in self.event_subscribers:
            try:
                if inspect.iscoroutinefunction(cb):
                    await cb(payload)
                else:
                    cb(payload)
            except Exception as e:
                logger.error(f"Error in subscriber event dispatch: {e}")

    async def _set_state(self, new_state: TaskState, data: Optional[Dict[str, Any]] = None):
        self.current_state = new_state
        if self.current_task_id:
            await task_memory.update_task_status(self.current_task_id, new_state.value, self.current_plan)
        await self._emit_event("state_change", data or {})

    async def run_command(self, user_request: str, session_id: str = "default_session") -> str:
        task_id = str(uuid.uuid4())
        self.current_task_id = task_id
        
        await short_term_memory.add_message(session_id, "user", user_request)

        # 1. UNDERSTANDING & CONTEXT
        await self._set_state(TaskState.UNDERSTANDING, {"request": user_request})
        ctx = await context_builder.build_context(session_id, user_request)

        # 2. PLANNING
        await self._set_state(TaskState.PLANNING, {"request": user_request})
        self.current_plan = await planner_provider.generate_plan(user_request, ctx)
        await task_memory.create_task(task_id, user_request, self.current_plan, self.current_state.value)
        await self._emit_event("plan_update", {"plan": self.current_plan})

        # 3. EXECUTE LOOP
        asyncio.create_task(self._process_plan_loop(session_id))
        return task_id

    async def _process_plan_loop(self, session_id: str, user_permission: Optional[bool] = None):
        for idx, step in enumerate(self.current_plan):
            if step.get("status") in ("completed", "failed"):
                continue

            # Set step to executing
            step["status"] = "executing"
            self.pending_step = step
            await self._set_state(TaskState.EXECUTING, {"step": step})

            # Run Executor
            res = await executor.execute_step(step, self.current_task_id, user_permission)

            if res.status == "WAITING_FOR_PERMISSION":
                step["status"] = "waiting_for_permission"
                self.pending_risk_level = res.risk_level
                await self._set_state(TaskState.WAITING_FOR_PERMISSION, {
                    "step": step,
                    "risk_level": res.risk_level.value,
                    "tool_name": step.get("tool_name"),
                    "arguments": step.get("arguments")
                })
                return  # Pause processing until approve/reject API is invoked

            if res.status == "REJECTED":
                step["status"] = "failed"
                step["error"] = res.error
                await self._set_state(TaskState.CANCELLED, {"reason": "Permission rejected by user"})
                return

            # OBSERVING & VERIFYING
            await self._set_state(TaskState.OBSERVING, {"step": step, "result": res.result})
            await self._set_state(TaskState.VERIFYING, {"step": step, "verified": res.success})

            if res.success:
                step["status"] = "completed"
                step["result"] = res.result
                await self._emit_event("tool_log", {"step": step, "result": res.result})
            else:
                step["status"] = "failed"
                step["error"] = res.error
                # Attempt recovery / replan
                await self._set_state(TaskState.RECOVERING, {"step": step, "error": res.error})
                # Single-step recovery attempt
                rec_success = await self._attempt_recovery(step, res.error)
                if not rec_success:
                    await self._set_state(TaskState.FAILED, {"failed_step": step, "error": res.error})
                    return

        # All steps complete
        await self._set_state(TaskState.COMPLETED, {"plan": self.current_plan})
        await short_term_memory.add_message(session_id, "assistant", f"Completed task '{self.current_task_id}' successfully.")
        await asyncio.sleep(2)
        await self._set_state(TaskState.IDLE)

    async def approve_permission(self):
        if self.current_state == TaskState.WAITING_FOR_PERMISSION and self.pending_step:
            await self._process_plan_loop("default_session", user_permission=True)

    async def reject_permission(self):
        if self.current_state == TaskState.WAITING_FOR_PERMISSION and self.pending_step:
            await self._process_plan_loop("default_session", user_permission=False)

    async def cancel_task(self):
        if self.current_task_id:
            await self._set_state(TaskState.CANCELLED, {"reason": "Cancelled by user"})
            await asyncio.sleep(1)
            await self._set_state(TaskState.IDLE)

    async def _attempt_recovery(self, failed_step: Dict[str, Any], error: Optional[str]) -> bool:
        # Fallback diagnostic logic: log error and check if safe to retry once
        if failed_step.get("retry_count", 0) < 1:
            failed_step["retry_count"] = failed_step.get("retry_count", 0) + 1
            logger.info(f"Retrying step '{failed_step.get('description')}' (Attempt {failed_step['retry_count']})")
            return False  # Mark failed for now to avoid infinite loops in Phase 1
        return False

orchestrator = AgentOrchestrator()
