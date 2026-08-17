from app.agent_loop.loop import RivaAgentLoop
from app.core.session import RivaSession
from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore
from app.orchestration.orchestrator import RivaOrchestrator
from app.tools.defaults import create_default_registry

database = "day9_contract.db"

orchestrator = RivaOrchestrator(
    registry=create_default_registry(),
    memory_manager=MemoryManager(
        MemoryStore(database)
    ),
)

loop = RivaAgentLoop(orchestrator)

session = RivaSession(
    session_id="day9-contract"
)

result = loop.run(
    session=session,
    user_input="Calculate 25 * 6",
)

print("RESPONSE:", result.response)
print("EXECUTIONS:", len(result.executions))

if result.executions:
    execution = result.executions[0]

    print("TOOL:", execution.tool_name)
    print("STATUS:", execution.status.value)
    print("RESULT:", execution.result)
    print("ERROR:", execution.error)
