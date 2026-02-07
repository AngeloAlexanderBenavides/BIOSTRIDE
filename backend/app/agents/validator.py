import base64
import os

from app.models.state import AuraState
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Initialize specialized model instance for validation
llmValidator = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.0
)


def validatorNode(state: AuraState) -> AuraState:
    """
    Agent: Validator (Bouncer)
    Role: Checks if the image contains a valid limb, stump, or subject (Human/Animal) suitable for a prosthesis.
    """
    print("--- 🛡️ VALIDATOR NODE ---")
    currentMessages = state.get("messages", [])

    try:
        raw_img = state.get("rawImage")
        if not raw_img:
            raise ValueError("No image data provided in state")

        # Encode image for Gemini
        img_base64 = base64.b64encode(raw_img).decode("utf-8")

        # Expanded prompt to include animals as requested
        promptText = """
        You are an expert biomechanical triage agent. Analyze this image.

        Determine the following:
        1. Does this image show a biological subject (human or animal) with a missing limb, amputation stump, or a context clearly requiring a prosthetic device?
        2. Identify the subject type: "HUMAN" or "ANIMAL".

        Strictly output your answer in this format:
        DECISION: [YES/NO]
        TYPE: [HUMAN/ANIMAL]
        REASON: [Brief explanation]
        """

        message = HumanMessage(
            content=[
                {"type": "text", "text": promptText},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{img_base64}"}}
            ]
        )

        response = llmValidator.invoke([message])
        content = response.content.strip()

        # Simple parsing
        decision = "YES" if "DECISION: YES" in content else "NO"
        subjectType = "ANIMAL" if "TYPE: ANIMAL" in content else "HUMAN"

        if decision == "YES":
            currentMessages.append(
                f"Validator: Approved. Subject identified as {subjectType}.")
            return {
                **state,
                "isValidLimb": True,
                "subjectType": subjectType,
                "nextStep": "analyst",  # Go to measurements
                "messages": currentMessages
            }
        else:
            currentMessages.append(f"Validator: REJECTED. {content}")
            return {
                **state,
                "isValidLimb": False,
                "nextStep": "end",
                "messages": currentMessages,
                "safetyNotes": ["Image rejected: No valid amputation or prosthetic context found."]
            }

    except Exception as e:
        print(f"Validation Error: {e}")
        # Default fail-safe
        return {
            **state,
            "nextStep": "end",
            "messages": currentMessages + [f"Validator: System Error {e}"]
        }
