


# """
# hr_graph.py
# """
# import sys
# import os
# current_dir = os.path.dirname(os.path.abspath(__file__))
# if current_dir not in sys.path:
#     sys.path.insert(0, current_dir)

# from langgraph.graph import StateGraph, END
# from state import HRState

# # Import Nodes
# from router_node import router_node
# from onboarding_node import onboarding_node
# from leave_node import leave_node
# from hr_rag_node import hr_rag_node
# from admin_leave_node import admin_leave_node
# from admin_onboarding_node import admin_onboarding_node # <--- NEW IMPORT

# def build_graph(db, retriever, llm):
#     workflow = StateGraph(HRState)

#     # 1. Add Nodes
#     workflow.add_node("router", router_node)
#     workflow.add_node("onboarding", onboarding_node)
#     workflow.add_node("leave", leave_node)
#     workflow.add_node("hr_rag", hr_rag_node)
#     workflow.add_node("admin_leave", admin_leave_node)
#     workflow.add_node("admin_onboarding", admin_onboarding_node) # <--- NEW NODE

#     # 2. Set Entry
#     workflow.set_entry_point("router")

#     # 3. Edges
#     workflow.add_conditional_edges(
#         "router",
#         lambda state: state["intent"],
#         {
#             "onboarding": "onboarding",
#             "leave": "leave",
#             "hr_query": "hr_rag",
#             "admin_leave": "admin_leave",
#             "admin_onboarding": "admin_onboarding" # <--- NEW EDGE
#         }
#     )

#     # 4. End Edges
#     workflow.add_edge("onboarding", END)
#     workflow.add_edge("leave", END)
#     workflow.add_edge("hr_rag", END)
#     workflow.add_edge("admin_leave", END)
#     workflow.add_edge("admin_onboarding", END)

#     return workflow.compile()

"""
hr_graph.py
"""
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from langgraph.graph import StateGraph, END
from state import HRState

# Import Nodes
from router_node import router_node
from onboarding_node import onboarding_node
from leave_node import leave_node
from hr_rag_node import hr_rag_node
from admin_onboarding_node import admin_onboarding_node
from admin_leave_node import admin_leave_node

# def decide_next_node(state):
#     role = state.get("role")
#     msg = state.get("message", "").lower()
    
#     if role == "admin":
#         # 1. PRIORITY: Explicit Leave Commands
#         if "leave" in msg:
#             return "admin_leave"
        
#         # 2. PRIORITY: Dashboard & Onboarding (Handles "Pending Requests" now)
#         if any(x in msg for x in [
#             "pending", "request", "dashboard", "show", "list", "search", "find",
#             "onboarding", "joiner", "remind", "finalize", "reject", "offer", "check"
#         ]):
#             return "admin_onboarding"
            
#         return "hr_rag"

#     if role == "employee":
#         if state.get("onboarding_active") is True:
#             return "onboarding"
#         if state.get("leave_draft") and len(state["leave_draft"]) > 0:
#             return "leave"
#         if any(x in msg for x in ["start", "yes", "begin", "fill details"]):
#             if state["db_user"].onboarding_status == "onboarding_triggered":
#                 return "onboarding"
#         if any(x in msg for x in ["leave", "sick", "vacation", "apply"]):
#             return "leave"
#         return "hr_rag"

#     return "hr_rag"

# def decide_next_node(state):
#     # Trust the intent set by the router_node
#     intent = state.get("intent")
#     role = state.get("role", "employee")

#     if role == "admin":
#         if intent == "admin_onboarding": return "admin_onboarding"
#         if intent == "admin_leave": return "admin_leave"
#         return "hr_rag"

#     # For Employees
#     if intent == "onboarding": return "onboarding"
#     if intent == "leave": return "leave"
    
#     # Everything else (details, balance, policy, chitchat) goes to RAG
#     return "hr_rag"


def decide_next_node(state):
    """
    Determines which node to visit next based on the intent
    calculated by the router_node.
    """
    intent = state.get("intent")
    
    # 1. Map intents to their respective nodes
    node_map = {
        "onboarding": "onboarding",
        "leave": "leave",
        "admin_onboarding": "admin_onboarding",
        "admin_leave": "admin_leave",
        "hr_query": "hr_rag"
    }
    
    # 2. Return the mapped node or default to RAG for safety
    return node_map.get(intent, "hr_rag")


def build_graph(db, retriever, llm):
    workflow = StateGraph(HRState)

    workflow.add_node("router", router_node)
    workflow.add_node("onboarding", onboarding_node)
    workflow.add_node("leave", leave_node)
    workflow.add_node("hr_rag", hr_rag_node)
    workflow.add_node("admin_onboarding", admin_onboarding_node)
    workflow.add_node("admin_leave", admin_leave_node)

    workflow.set_entry_point("router")

    workflow.add_conditional_edges(
        "router",
        decide_next_node,
        {
            "onboarding": "onboarding",
            "leave": "leave",
            "hr_rag": "hr_rag",
            "admin_onboarding": "admin_onboarding",
            "admin_leave": "admin_leave"
        }
    )

    workflow.add_edge("onboarding", END)
    workflow.add_edge("leave", END)
    workflow.add_edge("hr_rag", END)
    workflow.add_edge("admin_onboarding", END)
    workflow.add_edge("admin_leave", END)

    return workflow.compile()