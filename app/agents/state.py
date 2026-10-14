

"""
graph/state.py
Defines the shared state for the HR graph.
"""
from typing import TypedDict, List, Any, Optional

class HRState(TypedDict):
    # User Input/Context
    message: str
    user_id: str
    role: str
    intent: Optional[str]
    messages: List[dict]
    
    # Workflow Flags (Memory)
    onboarding_active: bool
    leave_draft: dict

    notification: Optional[str]
    
    # System Objects (passed around for easy access)
    db: Any
    retriever: Any
    llm: Any
    db_user: Any