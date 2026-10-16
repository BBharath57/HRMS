
# """
# router_node.py
# """
# def router_node(state):
#     message = state.get("message", "").lower().strip()
#     role = state.get("role", "employee")
    
#     # 1. Active Workflows (Priority)
#     if state.get("onboarding_active", False):
#         state["intent"] = "onboarding"
#         return state

#     if state.get("leave_draft") and len(state["leave_draft"]) > 0:
#         state["intent"] = "leave"
#         return state

#     # ... inside router_node.py ...

#     # 2. ADMIN COMMANDS (Stricter Logic)
#     if role == "admin":
#         if any(x in message for x in ["onboarding", "onbarding", "new user", "joining"]):
#             state["intent"] = "admin_onboarding"
#             return state
            
#         if any(x in message for x in ["leave", "time off", "vacation", "sick"]):
#             state["intent"] = "admin_leave"
#             return state
            
#         # FIX: Explicitly send "pending requests" to HR RAG (where we added the Smart Check)
#         if any(x in message for x in ["pending", "request", "show", "check", "any updates"]):
#             state["intent"] = "hr_query" # Let hr_rag_node handle the "Smart Check"
#             return state
            
#         # SAFETY: If admin just says "approve" or "check" without specifying what,
#         # do NOT default to leave. Send to HR_RAG to ask for clarification.
#         # (The previous code forced 'admin_leave' here, which caused your bug)

#     # 3. Employee Commands
#     if any(x in message for x in ["start onboarding", "begin onboarding", "join company", "reset onboarding"]):
#         state["intent"] = "onboarding"
#         return state
    
#     if any(x in message for x in ["apply leave", "request leave", "write email", "draft email"]):
#         state["intent"] = "leave"
#         return state
        
#     # 4. Default
#     state["intent"] = "hr_query"
#     return state


# """
# router_node.py
# """
# def router_node(state):
#     message = state.get("message", "").lower().strip()
#     role = state.get("role", "employee")

#     # 1. ACTIVE WORKFLOWS (HIGHEST PRIORITY)
#     if state.get("onboarding_active"):
#         state["intent"] = "onboarding"
#         return state

#     if state.get("leave_draft"):
#         state["intent"] = "leave"
#         return state

#     # 2. ADMIN ROUTING
#     if role == "admin":
#         # A. Greetings / Chitchat (Send to HR RAG for pure LLM response)
#         if message in ["hi", "hello", "hey", "ok", "okay", "thanks", "good", "great", "cool"]:
#             state["intent"] = "hr_query"
#             return state

#         # B. Onboarding Actions
#         if any(k in message for k in ["approve onboarding", "check onboarding", "new user", "joining"]):
#             state["intent"] = "admin_onboarding"
#             return state

#         # C. Leave Actions
#         if any(k in message for k in ["approve leaves", "check leaves", "vacation", "sick"]):
#             state["intent"] = "admin_leave"
#             return state

#         # D. Dashboard / Pending
#         if any(k in message for k in ["pending", "requests", "updates", "status"]):
#             state["intent"] = "admin_onboarding"
#             return state

#         # E. Data Inspection (Send to HR RAG Inspector)
#         if any(k in message for k in ["details", "profile", "info", "list", "show", "directory"]):
#             state["intent"] = "hr_query"
#             return state

#         # Default Admin
#         state["intent"] = "hr_query"
#         return state

#     # 3. EMPLOYEE ROUTING
#     if role == "employee":
#         # Onboarding Flow
#         if any(k in message for k in ["start onboarding", "join company", "reset onboarding"]):
#             state["intent"] = "onboarding"
#             return state

#         # FIX: "details" removed from here so it falls to hr_query (which has the "My Details" logic)
#         # We only keep "status" here for quick status checks
#         if "status" in message and "leave" not in message:
#             state["intent"] = "onboarding"
#             return state

#         # Leave Flow
#         if any(k in message for k in ["apply leave", "request leave", "leave status", "approved"]):
#             state["intent"] = "leave"
#             return state

#     # 4. DEFAULT (Falls to RAG/Chitchat)
#     state["intent"] = "hr_query"
#     return state


"""
router_node.py
# """
# def router_node(state):
#     message = state.get("message", "").lower().strip()
#     role = state.get("role", "employee")

#     # 1. ACTIVE WORKFLOWS (HIGHEST PRIORITY)
#     # If we are already in the middle of a form, keep us there!
#     if state.get("onboarding_active"):
#         state["intent"] = "onboarding"
#         return state

#     if state.get("leave_draft"):
#         state["intent"] = "leave"
#         return state

#     # 2. ADMIN ROUTING
#     if role == "admin":
#         if message in ["hi", "hello", "hey", "ok", "okay", "thanks", "good", "great"]:
#             state["intent"] = "hr_query"
#             return state

#         if any(k in message for k in ["approve onboarding", "check onboarding", "new user"]):
#             state["intent"] = "admin_onboarding"
#             return state

#         if any(k in message for k in ["approve leaves", "check leaves", "vacation"]):
#             state["intent"] = "admin_leave"
#             return state

#         if any(k in message for k in ["pending", "requests", "updates", "status"]):
#             state["intent"] = "admin_onboarding" # Dashboard
#             return state

#         if any(k in message for k in ["details", "profile", "info", "list", "show", "directory"]):
#             state["intent"] = "hr_query"
#             return state

#         state["intent"] = "hr_query"
#         return state

#    # 3. EMPLOYEE ROUTING (THE IMPROVED FIX)
#     if role == "employee":
#         # --- LEVEL 1: INFORMATION QUERIES (Priority) ---
#         # We check for balance/status FIRST so we don't accidentally start a form.
#         if any(k in message for k in ["balance", "remaining", "how many", "status", "check", "details", "info", "history"]):
#             state["intent"] = "hr_query"
#             return state

#         # --- LEVEL 2: ONBOARDING ---
#         if any(k in message for k in ["start onboarding", "join company", "reset onboarding", "begin onboarding"]):
#             state["intent"] = "onboarding"
#             return state

#         # --- LEVEL 3: APPLY ACTIONS (Strict Trigger) ---
#         # Only words that imply STARTING a request trigger the form wizard.
#         if any(k in message for k in ["apply", "request", "take leave", "vacation", "sick", "book"]):
#             state["intent"] = "leave"
#             return state

#         # Default to HR Query for general chitchat or unknown policy questions
#         state["intent"] = "hr_query"
#         return state















# def router_node(state):
    # message = state.get("message", "").lower().strip()
    # role = state.get("role", "employee")

    # # 1. Active Workflow Priority (Don't break a form mid-way)
    # if state.get("onboarding_active"):
    #     state["intent"] = "onboarding"
    #     return state
    # if state.get("leave_draft"):
    #     state["intent"] = "leave"
    #     return state

    # # 2. Employee Logic
    # if role == "employee":
    #     # Check for Information/Status FIRST
    #     info_keywords = ["how many", "balance", "remaining", "status", "check", "details", "info", "show"]
    #     if any(k in message for k in info_keywords):
    #         state["intent"] = "hr_query"
    #         return state

    #     # Check for Onboarding
    #     if any(k in message for k in ["onboarding", "join", "get started"]):
    #         state["intent"] = "onboarding"
    #         return state

    #     # Check for Application Action LAST
    #     if any(k in message for k in ["apply", "request", "take leave", "sick", "vacation"]):
    #         state["intent"] = "leave"
    #         return state

    # # 3. Admin Logic
    # if role == "admin":
    #     if any(k in message for k in ["pending", "approve", "reject", "requests"]):
    #         # Use a simple sub-routing for admin
    #         if "leave" in message: state["intent"] = "admin_leave"
    #         else: state["intent"] = "admin_onboarding"
    #         return state

    # # Default fallback
    # state["intent"] = "hr_query"
    # return state





"""
router_node.py
"""
def router_node(state):
    message = state.get("message", "").lower().strip()
    role = state.get("role", "employee")

    # 1. Active Workflow Priority
    if state.get("onboarding_active"):
        state["intent"] = "onboarding"
        return state
    
    if state.get("leave_draft"):
        state["intent"] = "leave"
        return state

    # 2. ADMIN ROUTING
    if role == "admin":
        # A. Info/Context Queries (Email, Balance, About) -> HR RAG
        if any(k in message for k in ["how many", "balance", "remaining", "email", "contact", "who is", "about"]):
            state["intent"] = "hr_query"
            return state

        if any(k in message for k in ["leave", "leaves", "vacation", "sick"]) and "details" not in message:
            state["intent"] = "admin_leave"
            return state

        # B. Dashboard & Actions -> Admin Onboarding Node
        # FIX: Explicitly added 'leaves', 'onboarding', 'remind', 'finalize', 'reject'
        admin_keywords = [
            "pending", "dashboard", "show", "list", "details", "give", "profile", 
            "onboard", "new employee", "remind", "finalize", "reject", 
            "leaves", "onboarding", "requests", "joiners"
        ]
        
        if any(k in message for k in admin_keywords):
            state["intent"] = "admin_onboarding"
            return state

        # # C. Explicit Leave Actions (Approve/Reject) -> Admin Leave Node
        # if any(k in message for k in ["approve", "leave", "vacation"]) and "details" not in message:
        #     state["intent"] = "admin_leave"
        #     return state
        
        # D. Fallback
        state["intent"] = "hr_query"
        return state

    # 3. EMPLOYEE ROUTING
    if role == "employee":
        if any(k in message for k in ["how many", "balance", "remaining", "status", "check", "details", "info", "email"]):
            state["intent"] = "hr_query"
            return state

        if any(k in message for k in ["start onboarding", "join", "begin"]):
            state["intent"] = "onboarding"
            return state

        if any(k in message for k in ["apply", "request", "take leave", "sick", "vacation"]):
            state["intent"] = "leave"
            return state

    # Default
    state["intent"] = "hr_query"

    # ADD THIS LINE RIGHT HERE:
    print(f"🕵️ DEBUG ROUTER: Message='{message}' | Routed Intent='{state.get('intent')}'")
    return state