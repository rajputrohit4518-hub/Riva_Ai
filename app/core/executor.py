from app.core.execution import ExecutionResult, ExecutionStatus
from app.security.audit import AuditLogger
from app.tools.registry import ToolRegistry


class ExecutionEngine:
    def __init__(
        self,
        registry: ToolRegistry,
        audit_logger: AuditLogger | None = None,
    ) -> None:
        self._registry = registry
        self._audit = audit_logger or AuditLogger()

    def execute(self, tool_name: str, **kwargs) -> ExecutionResult:
        execution = ExecutionResult(tool_name=tool_name)

        try:
            result = self._registry.execute(tool_name, **kwargs)

            execution.result = result
            execution.status = ExecutionStatus.SUCCESS

        except PermissionError as exc:
            execution.status = ExecutionStatus.DENIED
            execution.error = str(exc)

        except Exception as exc:
            execution.status = ExecutionStatus.FAILED
            execution.error = str(exc)

        finally:
            execution.complete()

            event = self._audit.create_event(
                execution_id=execution.execution_id,
                tool_name=execution.tool_name,
                status=execution.status.value,
                result=execution.result,
                error=execution.error,
            )

            self._audit.record(event)

        return execution
