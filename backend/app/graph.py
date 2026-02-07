from langgraph.graph import END, StateGraph

from app.agents.analyst import anatomicalAnalystNode
from app.agents.designer import designEngineerNode
from app.agents.prompt_engineer import promptEngineerNode
from app.agents.safety import safetyAuditorNode
from app.agents.supervisor import supervisorNode
from app.agents.technical_writer import technicalWriterNode
from app.agents.validator import validatorNode
from app.agents.visualizer import visualizerNode
from app.models.state import AuraState


def buildInfoGraph():
    workflow = StateGraph(AuraState)

    # 1. Add All Nodes
    workflow.add_node("supervisor", supervisorNode)
    workflow.add_node("validator", validatorNode)
    workflow.add_node("analyst", anatomicalAnalystNode)
    workflow.add_node("prompt_engineer", promptEngineerNode)
    workflow.add_node("visualizer", visualizerNode)
    workflow.add_node("designer", designEngineerNode)
    workflow.add_node("safety", safetyAuditorNode)
    workflow.add_node("technical_writer", technicalWriterNode)

    # 2. Set Entry Point
    workflow.set_entry_point("supervisor")

    # 3. Router Logic
    def routeStep(state: AuraState):
        step = state.get("nextStep", END)
        if step == "validate":
            return "validator"
        if step == "analyst":
            return "analyst"
        if step == "prompt_engineer":
            return "prompt_engineer"
        if step == "visualizer":
            return "visualizer"
        if step == "design":
            return "designer"  # Normalized name
        if step == "designer":
            return "designer"
        if step == "safety":
            return "safety"
        if step == "technical_writer":
            return "technical_writer"
        return END

    # 4. Define Edges

    # Supervisor -> Validator
    workflow.add_conditional_edges(
        "supervisor",
        routeStep,
        {"validator": "validator", END: END}
    )

    # Validator -> Analyst (or BLOCK/END)
    workflow.add_conditional_edges(
        "validator",
        routeStep,
        {"analyst": "analyst", END: END}
    )

    # Analyst -> Prompt Engineer
    workflow.add_edge("analyst", "prompt_engineer")

    # Prompt Engineer -> Visualizer
    workflow.add_edge("prompt_engineer", "visualizer")

    # Visualizer -> Designer
    workflow.add_edge("visualizer", "designer")

    # Designer -> Safety
    workflow.add_edge("designer", "safety")

    # Safety -> Technical Writer OR Loop back
    workflow.add_conditional_edges(
        "safety",
        routeStep,
        {"designer": "designer", "technical_writer": "technical_writer", END: END}
    )

    # Technical Writer -> END
    workflow.add_edge("technical_writer", END)

    return workflow.compile()


# Validated Graph Instance
auraGraph = buildInfoGraph()
