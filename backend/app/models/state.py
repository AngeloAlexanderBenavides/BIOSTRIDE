from typing import Any, Dict, List, Optional, TypedDict


class AuraState(TypedDict):
    """
    State definition for the AuraPrint AI graph.
    Using camelCase for keys as per project instructions.
    """
    rawImage: Optional[bytes]          # Original photo
    referenceScale: float              # mm per pixel

    # User Inputs
    limbConfiguration: str             # "Below Knee" / "Above Knee"
    activityLevel: List[str]           # "Walk", "Run", "Sport", etc. (Multi-select)
    userNotes: str                     # Special prompts from user

    # AI Generated Content
    isValidLimb: bool                  # Validator output
    subjectType: Optional[str]         # "Human" or "Animal"
    anatomicalFeatures: Dict[str, Any]  # Measurements

    # Image Gen (Multimodal)
    visualPrompt: str                  # Prompt for Image Gen Agent
    prosthesisImageUrl: str            # Generated visual preview (Nano Banana/Imagen)
    tryOnImageUrl: str                 # Composite image

    # Engineering & DIY
    designParameters: Dict[str, Any]   # CAD params
    stlPath: Optional[str]             # Path to STL
    assemblyGuide: str                 # DIY markdown instructions

    safetyNotes: List[str]             # Safety warnings
    nextStep: str                      # Flow control (Router)
    messages: List[str]                # Conversation/Log history
