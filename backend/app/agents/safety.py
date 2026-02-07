from app.models.state import AuraState
from langgraph.graph import END


def safetyAuditorNode(state: AuraState) -> AuraState:
    """
    Agent: Safety Auditor
    Role: Reviews parameters and image context before final release.
    """
    print("--- 🦺 SAFETY AUDITOR NODE ---")
    designParams = state.get("designParameters", {})
    thickness = designParams.get("wallThicknessMm", 0)
    currentMessages = state["messages"]
    safetyNotes = state.get("safetyNotes", [])

    # Check rule: Thickness < 3mm is unsafe
    if thickness < 3.0:
        errorMsg = "Critical: Wall thickness insufficient (< 3mm)."
        safetyNotes.append(errorMsg)
        currentMessages.append(f"Safety: {errorMsg} Sending back to design.")
        return {
            **state,
            "safetyNotes": safetyNotes,
            "nextStep": "design",  # Loop back
            "messages": currentMessages
        }

    currentMessages.append("Safety: Design approved. Ready for documentation.")

    return {
        **state,
        "safetyNotes": safetyNotes,
        "nextStep": "technical_writer",
        "messages": currentMessages
    }
