import base64
import json
import logging
import os

from app.models.state import AuraState
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
logger = logging.getLogger(__name__)

# We use Gemini Vision to analyze dimensions and condition
llmAnalyst = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.0
)


def anatomicalAnalystNode(state: AuraState) -> AuraState:
    """
    Agent: Vision Analyst
    Role: Extracts anatomical features and estimates measurements from the image using Computer Vision (Gemini).
    """
    logger.info("--- 👁️ VISION ANALYST NODE ---")

    current_messages = state.get("messages", [])
    raw_img = state.get("rawImage")
    subject = state.get("subjectType", "HUMAN")

    if not raw_img:
        logger.warning("Analyst: No image found, using default data.")
        return state

    # Vision Prompt
    prompt = f"""
    Analyze this image of a {subject} limb/stump for prosthetic fitting.

    Task:
    Estimate the following anatomical features based on visual proportions (assume standard reference).

    Output JSON ONLY:
    {{
        "stumpLengthMm": <estimated_number>,
        "circumferenceMm": <estimated_number>,
        "shape": "<'conical'|'cylindrical'|'bulbous'|'irregular'>",
        "skinTone": "<description>",
        "visualCondition": "<healthy|scarred|swollen>"
    }}
    """

    features = {}

    try:
        # Properly encode bytes to base64 string
        if isinstance(raw_img, bytes):
            b64_str = base64.b64encode(raw_img).decode('utf-8')
        else:
            # Assume it might already be base64 string
            b64_str = str(raw_img)

        msg = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": f"data:image/jpeg;base64,{b64_str}"}
            ]
        )

        response = llmAnalyst.invoke([msg])
        content = response.content.replace("```json", "").replace("```", "").strip()

        features = json.loads(content)
        logger.info(f"Analyst Extracted: {features}")

        current_messages.append(
            f"Analyst: Extracted features - {features.get('shape')} shape, ~{features.get('stumpLengthMm')}mm length.")

    except Exception as e:
        logger.error(f"Analyst Error: {e}", exc_info=True)
        # Fallback if Gemini fails or quota exceeded
        features = {
            "stumpLengthMm": 150.0,
            "circumferenceMm": 280.0,
            "shape": "conical",
            "type": state.get("limbConfiguration", "Unknown")
        }
        current_messages.append(
            "Analyst: Vision analysis failed, using fallback metrics.")

    return {
        **state,
        "anatomicalFeatures": features,
        "messages": current_messages,
        "nextStep": "prompt_engineer" # Explicitly routing to next step
    }
