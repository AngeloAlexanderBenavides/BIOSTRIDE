import logging
import os
from pathlib import Path
from typing import List, Optional

from app.graph import auraGraph
from app.models.state import AuraState
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="BIOSTRIDE API")

# --- CORS & Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Path Configuration ---
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
FRONTEND_DIR = BASE_DIR.parent / "frontend"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/api/process-design")
async def process_design(
    image: UploadFile = File(...),
    limbConfig: str = Form("Not specified"),
    activity: List[str] = Form([]),
    notes: str = Form("")
):
    """
    Main Endpoint: Processes the uploaded image and user preferences through the BIOSTRIDE AI Agent Graph.
    """
    try:
        logger.info(f"Processing design request for file: {image.filename}")
        
        # Read the image bytes
        image_bytes = await image.read()

        # Initialize State
        initial_state: AuraState = {
            "rawImage": image_bytes,
            "referenceScale": 0.0,
            
            # User Inputs
            "limbConfiguration": limbConfig,
            "activityLevel": activity,
            "userNotes": notes,

            # Internal System Data
            "anatomicalFeatures": {},
            "designParameters": {},
            "stlPath": "",
            "safetyNotes": [],
            "nextStep": "",
            "messages": [f"System: Received image {image.filename}"]
        }

        # Execute Graph
        final_state = await auraGraph.ainvoke(initial_state)

        # Create Response (Remove binary data)
        response_state = final_state.copy()
        response_state.pop("rawImage", None) 

        return JSONResponse(content=response_state)

    except Exception as e:
        logger.error(f"Error processing design: {str(e)}", exc_info=True)
        return JSONResponse(content={"error": str(e)}, status_code=500)

# --- Static Files Mounting ---
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")

if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")
else:
    logger.warning(f"Frontend directory not found at {FRONTEND_DIR}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
