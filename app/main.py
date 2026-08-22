from app.runtime.runtime import RivaRuntime
from app.core.session import RivaSession
from app.memory.manager import MemoryManager
from app.tools.defaults import create_default_registry


def main() -> None:
    registry = create_default_registry()
    memory = MemoryManager()
    session = RivaSession(session_id="riva-cli")

    runtime = RivaRuntime(
        registry=registry,
        memory_manager=memory,
    )

    print("=" * 60)
    print("Riva — Personal AI Assistant")
    print("Type 'exit' or 'quit' to stop.")
    print("=" * 60)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nRiva stopped.")
            break

        if user_input.lower() in {"exit", "quit"}:
            print("Riva stopped.")
            break

        if not user_input:
            continue

        try:
            result = runtime.handle(
                session=session,
                user_input=user_input,
            )

            print(f"Riva: {result.response}")

        except Exception as exc:
            print(f"Riva: Error: {exc}")


if __name__ == "__main__":
    main()
