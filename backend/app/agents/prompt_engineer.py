import os

from app.models.state import AuraState
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llmPrompter = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # Using Flash to save quota, but still 2.5 smarts
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7
)


def promptEngineerNode(state: AuraState) -> AuraState:
    """
    Agent: Prompt Engineer
    Role: Crafts valid, high-quality prompts for the Image Generation Agent.
    """
    print("--- ✍️ PROMPT ENGINEER NODE ---")

    # Gather Context
    subject = state.get("subjectType", "HUMAN")
    features = state.get("anatomicalFeatures", {})
    activities = ", ".join(state.get("activityLevel", []))
    userNotes = state.get("userNotes", "")
    limbConfig = state.get("limbConfiguration", "Prosthesis")

    # Construct Meta-Prompt
    system_instruction = """
    You are an expert AI Art Prompt Engineer. Your goal is to create a detailed, photorealistic prompt
    for an image generation model (like Stable Diffusion or Imagen).

    The prompt should describe a futuristic, functional, and aesthetic prosthetic limb.
    Focus on materials (carbon fiber, titanium, voronoi patterns), lighting, and context.
    If the user has special requests (e.g. "Iron Man style"), incorporate them creatively.

    Output ONLY raw prompt text. No "Here is the prompt:" prefix.
    """

    user_context = f"""
    Subject: {subject}
    Limb Type: {limbConfig}
    Anatomical Features: {features}
    Intended Activities: {activities}
    User Special Requests: {userNotes}

    Create a prompt for a standalone product shot of this prosthesis.
    """

    response = llmPrompter.invoke([
        SystemMessage(content=system_instruction),
        HumanMessage(content=user_context)
    ])

    generated_prompt = response.content.strip()

    currentMessages = state["messages"]
    currentMessages.append("Prompt Engineer: Creative prompt generated.")

    return {
        **state,
        "visualPrompt": generated_prompt,
        "nextStep": "visualizer",
        "messages": currentMessages
    }
