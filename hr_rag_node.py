"""
hr_rag_node.py
"""
from rag_pipeline import retriever, llm
from models import Employee, LeaveRequest
from sqlalchemy import desc

HELP_MENU = {
    "employee": "👋 **Commands:**\n- `How many leaves left?` \n- `Show my details` \n- `Apply for leave` ",
    "admin": "👑 **Admin Commands:**\n- `List all employees` \n- `Show [Name] details` \n- `Show pending requests` "
}

chitchat_map = {
    "okay": "Glad I could help!",
    "fine": "Great! I'm here if you need anything else.",
    "thanks": "You're welcome!",
}

def get_employee_context(db, employee):
    """
    FIX: Added Email, Personal Email, and ID to context.
    """
    if not employee: return "User not found."

    paid_left = 1 - employee.used_paid_leaves
    emergency_left = 1 - employee.used_emergency_leaves
    last_leave = db.query(LeaveRequest).filter(LeaveRequest.employee_id == employee.id).order_by(desc(LeaveRequest.created_at)).first()
    leave_status = f"{last_leave.leave_type} ({last_leave.status})" if last_leave else "None"

    # Included Emails here so RAG can answer "give me email"
    return (f"Name: {employee.name}, Role: {employee.role}, "
            f"Email: {employee.email}, ID: {employee.employee_id_str or 'N/A'}, "
            f"Paid Leaves: {paid_left}/1, Emergency: {emergency_left}/1, Last Request: {leave_status}")

def check_notifications(db, user_id, role):
    # Only for Employee unseen updates
    if role == "employee":
        emp = db.query(Employee).filter(Employee.email == user_id).first()
        if emp:
            last = db.query(LeaveRequest).filter(LeaveRequest.employee_id == emp.id, LeaveRequest.notification_seen == False).order_by(desc(LeaveRequest.created_at)).first()
            if last and last.status in ["approved", "rejected"]:
                last.notification_seen = True
                db.commit()
                return f"✨ **Update:** Your leave for {last.start_date.date()} was **{last.status.upper()}**."
    return "None"

def format_chat_history(messages):
    history = ""
    recent = messages[-4:] 
    for msg in recent:
        role = "User" if msg["role"] == "user" else "Assistant"
        content = str(msg["content"])[:200]
        history += f"{role}: {content}\n"
    return history

def hr_rag_node(state):
    db = state["db"]
    user_input = state["message"]
    user_email = state["user_id"]
    role = state.get("role", "employee")
    messages = state.get("messages", [])

    # Static Responses
    if user_input.lower() in ["help", "commands"]:
        return {"messages": state["messages"] + [{"role": "assistant", "content": HELP_MENU.get(role)}]}
    if user_input.lower() in chitchat_map:
        return {"messages": state["messages"] + [{"role": "assistant", "content": chitchat_map[user_input.lower()]}]}

    # Data Retrieval
    current_user_obj = db.query(Employee).filter(Employee.email == user_email).first()
    my_context = get_employee_context(db, current_user_obj)
    
    # Target Context (for Admin queries like "give me ravi details")
    target_emp_context = "None"
    directory_data = "None"
    
    # if role == "admin":
    #     if "list" in user_input.lower() or "directory" in user_input.lower():
    #         all_emps = db.query(Employee).all()
    #         directory_data = "| Name | Role | Status | Email |\n|---|---|---|\n"
    #         for e in all_emps: directory_data += f"| {e.name} | {e.role} | {e.onboarding_status} | {e.email} |\n"
    #     else:
    #         # Smart Search: Look for names in the prompt
    #         for emp in db.query(Employee).all():
    #             if emp.name.lower() in user_input.lower() and len(user_input) > 4:
    #                 target_emp_context = get_employee_context(db, emp)
    #                 break

    if role == "admin":
        # FIX 1: Broadened the keywords to catch "all employees"
        if any(kw in user_input.lower() for kw in ["list", "directory", "all employee", "everyone", "all the employee"]):
            all_emps = db.query(Employee).all()
            # FIX 2: Added the Email column to the directory string!
            directory_data = "| Name | Role | Status | Email |\n|---|---|---|---|\n"
            for e in all_emps: 
                directory_data += f"| {e.name} | {e.role} | {e.onboarding_status} | {e.email} |\n"
        else:
            # FIX 3: Removed the 'break' statement so it finds MULTIPLE people
            found_contexts = []
            for emp in db.query(Employee).all():
                if emp.name.lower() in user_input.lower() and len(emp.name) > 2:
                    found_contexts.append(get_employee_context(db, emp))
            
            if found_contexts:
                # Join all found employees together
                target_emp_context = "\n---\n".join(found_contexts)

    docs = retriever.invoke(user_input)
    chat_history = format_chat_history(messages)
    
    notif = check_notifications(db, user_email, role)
    notif_section = f"NOTIFICATIONS: {notif}" if notif != "None" else ""

    # FIX: Prompt Instructions to stop repetitive naming
    prompt = f"""You are VoltaBot, a professional HR Assistant.
    
    --- CONTEXT ---
    CURRENT USER: {current_user_obj.name} ({role})
    MY DATA: {my_context}
    TARGET USER DATA: {target_emp_context} (Use this if user asks about someone else)
    DIRECTORY: {directory_data}
    POLICIES: {" ".join([d.page_content for d in docs])}
    {notif_section}
    
    --- HISTORY ---
    {chat_history}

    --- INSTRUCTIONS ---
    1. Answer the question based on the Context or Policies.
    2. If asked about another employee (e.g. "email of ravi"), use TARGET USER DATA.
    3. If asked about leaves/balance, use MY DATA (or TARGET DATA if Admin).
    4. **Tone:** Friendly but professional. Do NOT repeat the user's name in every sentence. Only use it if necessary for clarity.
    5. Be concise.

    QUESTION: {user_input}"""
    
    response = llm.invoke(prompt).content
    return {
        **state, 
        "messages": state["messages"] + [{"role": "assistant", "content": response}]
    }


# """
# hr_rag_node.py
# """
# from models import Employee, Onboarding, LeaveRequest
# import re


# def hr_rag_node(state):
#     if "messages" not in state:
#         state["messages"] = []

#     user_input = state.get("message", "").strip()
#     ui_lower = user_input.lower()

#     llm = state.get("llm")
#     retriever = state.get("retriever")
#     db = state["db"]
#     user_id = state["user_id"]
#     role = state.get("role", "employee")


#     # -----------------------------
#     # 1. GREETING
#     # -----------------------------
#     if re.search(r"\b(hi|hello|hey)\b", ui_lower):
#         state["messages"].append({
#             "role": "assistant",
#             "content": "👋 Hello!"
#         })
#         return state

#     # -----------------------------
#     # 2. CHITCHAT
#     # -----------------------------
#     if ui_lower in ["ok", "okay", "thanks", "cool"]:
#         state["messages"].append({
#             "role": "assistant",
#             "content": "You're welcome!"
#         })
#         return state

#     # -----------------------------
#     # 3. TRUE RAG ONLY (POLICY / WHAT / WHY)
#     # -----------------------------
#     docs = retriever.invoke(user_input)
#     context = "\n".join(d.page_content for d in docs)

#     prompt = f"""
# Context:
# {context}

# Question:
# {user_input}

# Answer clearly and concisely:
# """

#     response = llm.invoke(prompt)

#     state["messages"].append({
#         "role": "assistant",
#         "content": response.content
#     })
#     return state
