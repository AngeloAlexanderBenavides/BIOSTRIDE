import logging
import os
import uuid
from pathlib import Path

from app.models.state import AuraState
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
logger = logging.getLogger(__name__)

def visualizerNode(state: AuraState) -> AuraState:
    """
    Agent: Visualizer (Image Generator)
    Role: Uses Gemini 2.5 Flash Image (Nano Banana) to generate prosthetic previews.
    
    Args:
        state: The current state of the design process.
        
    Returns:
        AuraState: Updated state with the generated image URL (prosthesisImageUrl, tryOnImageUrl).
    """
    logger.info("--- 🎨 VISUALIZER NODE (Nano Banana) ---")

    prompt = state.get("visualPrompt", "")
    current_messages = state.get("messages", [])

    # Configuration for Gemini (Nano Banana)
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    generated_url = ""

    if GOOGLE_API_KEY:
        try:
            logger.info(f"Sending prompt to Gemini Nano Banana: {prompt[:50]}...")

            client = genai.Client(api_key=GOOGLE_API_KEY)

            response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_modalities=['IMAGE']
                )
            )

            if response.parts:
                for part in response.parts:
                    if part.inline_data:
                        # part.as_image() returns a PIL Image
                        img = part.as_image()

                        # Configure Output Path using Pathlib
                        # Logic: From agents/visualizer.py -> app/agents -> backend/app -> backend/
                        base_dir = Path(__file__).resolve().parent.parent.parent
                        output_dir = base_dir / "output"
                        output_dir.mkdir(parents=True, exist_ok=True)
                        
                        filename = f"gen_{uuid.uuid4().hex}.png"
                        output_path = output_dir / filename

                        img.save(output_path)

                        generated_url = f"/outputs/{filename}"
                        logger.info(f"Image generated successfully: {filename}")
                        break  # Only save the first image

            if not generated_url:
                logger.warning("No image returned by API. Falling back to mock.")
                raise ValueError("No image part in response")

        except Exception as e:
            logger.error(f"Visualizer API Error: {e}", exc_info=True)
            generated_url = "/static/mock_prosthesis_human.png"
    else:
        logger.warning("No GOOGLE_API_KEY found. Using Mock.")
        if state.get("subjectType") == "ANIMAL":
            generated_url = "/static/mock_prosthesis_animal.png"
        else:
            generated_url = "/static/mock_prosthesis_human.png"

    current_messages.append("Visualizer: Prosthetic preview generated.")

    return {
        **state,
        "prosthesisImageUrl": generated_url,
        "tryOnImageUrl": generated_url,
        "nextStep": "designer",
        "messages": current_messages
    }
