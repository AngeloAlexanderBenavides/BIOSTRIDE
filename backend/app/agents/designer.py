import os
import time

import numpy as np
from app.models.state import AuraState
from dotenv import load_dotenv
from stl import mesh

load_dotenv()

# Note: llmWriter moved to technical_writer.py


def designEngineerNode(state: AuraState) -> AuraState:
    """
    Agent: Biomechanical Engineer
    Role: Generates STL file AND a DIY assembly guide.
    """
    print("--- 📐 DESIGN ENGINEER NODE ---")
    features = state["anatomicalFeatures"]
    stumpLength = features.get("stumpLengthMm", 150.0)
    subject = state.get("subjectType", "HUMAN")

    # --- PART 1: STL GENERATION ---
    parameters = {
        "material": "TPU" if "Run" in state.get("activityLevel", []) else "PLA",
        "wallThicknessMm": 5.0,
        "density": "Variable"
    }

    currentMessages = state["messages"]
    webPath = ""

    try:
        # Load Base Model
        # PRO TIP: You should have different base models for Animals vs Humans
        base_asset = "base_socket.stl"

        baseModelPath = os.path.join(os.path.dirname(
            __file__), "..", "..", "assets", "base_models", base_asset)

        if not os.path.exists(baseModelPath):
            # Checking fallback for dev environment
            # If assets/base_models doesn't exist, we create a dummy cube for the demo
            print(f"Base model not found at {baseModelPath}, creating dummy...")

            # Create a simple cube using numpy-stl logic if file missing
            data = np.zeros(6, dtype=mesh.Mesh.dtype)
            your_mesh = mesh.Mesh(data, remove_empty_areas=False)
            # (Mock mesh creation omitted for brevity, usually we'd load a file)
            # Let's assume the file exists or handle error gracefully
            pass

        # Loading logic (Placeholder for robust mesh loading)
        # your_mesh = mesh.Mesh.from_file(baseModelPath)

        # Saving Dummy Output for connection test
        outputDir = os.path.join(os.path.dirname(__file__), "..", "..", "output")
        os.makedirs(outputDir, exist_ok=True)

        timestamp = int(time.time())
        filename = f"prosthesis_{subject}_{timestamp}.stl"
        outputPath = os.path.join(outputDir, filename)

        # Mock save if mesh not loaded
        with open(outputPath, 'w') as f:
            f.write("Solid STL ASCII...")  # Dummy header

        # Relative path for frontend
        webPath = f"outputs/{filename}"
        currentMessages.append(
            f"Designer: Generated STL for {subject} at {stumpLength}mm.")

    except Exception as e:
        print(f"Design Error: {e}")
        webPath = "error_generating_file"

    # --- PART 2: OUTPUT ---
    # The drafting logic has been moved to technical_writer.py

    return {
        **state,
        "designParameters": parameters,
        # "designReasoning": ... (Handled by Writer now)
        "stlPath": webPath,
        "nextStep": "safety",
        "messages": currentMessages
    }
