import os

from app.models.state import AuraState
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# We use the text model to generate the guide
llmWriter = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)


def technicalWriterNode(state: AuraState) -> AuraState:
    """
    Agent: Technical Writer / Advisor
    Role: Analyzes the engineering parameters and writes a user-friendly guide and technical reasoning in Spanish.
    """
    print("--- ✍️ TECHNICAL WRITER NODE ---")

    subject = state.get("subjectType", "HUMAN")
    activity_level = state.get("activityLevel", "Unknown")
    # We take the parameters decided by the Engineer
    parameters = state.get("designParameters", {})
    material_engineer = parameters.get("material", "PLA")
    thickness_engineer = parameters.get("wallThicknessMm", 5.0)

    # --- DIY GUIDE GENERATION AND REASONING ---
    guide_prompt = f"""
    You are a biomechanical advisor. The engineer has already designed the part.

    Context:
    - Subject: {subject}
    - Activity: {activity_level}
    - Engineer's Choice: Material {material_engineer}, Thickness {thickness_engineer}mm.

    Task:
    Explain *why* this choice is good and provide an assembly guide.
    IMPORTANT: Write the CONTENT in SPANISH (Español), but keep the KEYS in English.

    Output exactly this format (no markdown code blocks):
    REASONING: [1 sentence technical justification in Spanish explaining the engineer's choice]
    PRIMARY_MATERIAL: [Confirm the material {material_engineer} or refine the name]
    ALTERNATIVE_MATERIAL: [Suggest a fallback material] | [Short reason in Spanish]
    GUIDE:
    [Markdown guide here in Spanish covering Printing, Post-Processing, Assembly]
    """

    try:
        response = llmWriter.invoke([HumanMessage(content=guide_prompt)])
        content = response.content

        # Robust Parsing
        reasoning = "Optimización completa."
        primary_mat = material_engineer
        alt_mat = "PLA+ | Estructura rígida"
        assembly_guide = "Error generando la guía."

        lines = content.split('\n')
        guide_start = False
        guide_lines = []

        for line in lines:
            if line.startswith("REASONING:"):
                reasoning = line.replace("REASONING:", "").strip()
            elif line.startswith("PRIMARY_MATERIAL:"):
                primary_mat = line.replace("PRIMARY_MATERIAL:", "").strip()
            elif line.startswith("ALTERNATIVE_MATERIAL:"):
                alt_mat = line.replace("ALTERNATIVE_MATERIAL:", "").strip()
            elif line.startswith("GUIDE:"):
                guide_start = True
            elif guide_start:
                guide_lines.append(line)

        if guide_lines:
            assembly_guide = "\n".join(guide_lines).strip()

    except Exception as e:
        print(f"Writer Error: {e}")
        reasoning = "Error en el análisis."
        primary_mat = material_engineer
        alt_mat = "N/A"
        assembly_guide = "No guide available."

    # We update the state with the enriched text data
    # Note: We preserve the numerical parameters from the engineer
    currentMessages = state.get("messages", [])
    currentMessages.append("Writer: Technical guide and reasoning generated.")

    return {
        **state,
        "designReasoning": reasoning,
        # We can update the material name if the writer gives a more specific one (e.g., "TPU Shore 95A")
        "designParameters": {**parameters, "material": primary_mat},
        "alternativeMaterial": alt_mat,
        "assemblyGuide": assembly_guide,
        "messages": currentMessages
    }
