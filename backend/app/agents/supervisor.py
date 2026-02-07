from app.models.state import AuraState


def supervisorNode(state: AuraState) -> AuraState:
    """
    Agent: Supervisor (Entry Point)
    Role: Receives request and routes to first validation step.
    """
    print("--- 🤖 SUPERVISOR NODE ---")
    currentMessages = state.get("messages", [])
    currentMessages.append("Supervisor: Workflow started. Routing to Validator.")

    return {
        **state,
        "nextStep": "validate",
        "messages": currentMessages
    }
