# local best
# """
# leave_node.py
# """
# from models import LeaveRequest, Employee
# from datetime import datetime
# from email_service import send_email
# import re

# APP_LINK = "http://localhost:8501"
# ADMIN_EMAIL = "bharathkumarking143@gmail.com" # Hardcoded Admin

# def is_valid_date(date_str):
#     return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", date_str.strip()))

# def calculate_days(start_str, end_str, duration_type):
#     s = datetime.strptime(start_str, "%Y-%m-%d")
#     e = datetime.strptime(end_str, "%Y-%m-%d")
#     days = (e - s).days + 1
#     if duration_type == "half day":
#         return 0.5
#     return float(days)

# def leave_node(state):
#     db = state["db"]
#     message = state.get("message", "").strip()
#     user_email = state["user_id"]
#     llm = state.get("llm")
    
#     employee = db.query(Employee).filter(Employee.email == user_email).first()
#     user_name = employee.name if employee and employee.name else "Employee"
#     leave_draft = state.get("leave_draft") or {}
#     response = ""

#     # --- 0. CANCEL COMMAND ---
#     cancel_triggers = ["cancel", "stop", "abort", "exit", "quit", "end"]
#     if any(x in message.lower() for x in cancel_triggers):
#         return {
#             **state, 
#             "leave_draft": {}, 
#             "messages": state["messages"] + [{"role": "assistant", "content": "❌ **Process Stopped.** Request cancelled."}]
#         }

#     # ============================================================
#     # STEP 1: START DATE
#     # ============================================================
#     if not leave_draft.get("step"):
#         leave_draft["step"] = "start_date"
#         response = "📅 **Step 1:** What is the **Start Date**? (YYYY-MM-DD)"

#     # ============================================================
#     # STEP 2: END DATE
#     # ============================================================
#     elif leave_draft["step"] == "start_date":
#         if is_valid_date(message):
#             leave_draft["start_date"] = message
#             leave_draft["step"] = "end_date"
#             response = "📅 **Step 2:** What is the **End Date**? (YYYY-MM-DD)"
#         else:
#             response = "⚠️ Invalid format. Please use **YYYY-MM-DD** (e.g., 2025-02-20)."

#     # ============================================================
#     # STEP 3: LEAVE TYPE
#     # ============================================================
#     elif leave_draft["step"] == "end_date":
#         if is_valid_date(message):
#             if message < leave_draft["start_date"]:
#                 response = "⚠️ **Error:** End date cannot be before Start date."
#             else:
#                 leave_draft["end_date"] = message
#                 leave_draft["step"] = "type"
#                 response = "📋 **Step 3:** What type of leave is this?\n(Options: **Emergency** or **Unpaid**)"
#         else:
#             response = "⚠️ Invalid format. Please use **YYYY-MM-DD**."

#     # ============================================================
#     # STEP 4: DURATION
#     # ============================================================
#     elif leave_draft["step"] == "type":
#         selected = message.lower().strip()
#         if selected not in ["unpaid", "emergency"]:
#             response = "⚠️ Invalid type. Please choose: **Emergency** or **Unpaid**."
#         else:
#             leave_draft["type"] = selected
#             leave_draft["step"] = "duration"
#             response = "⏳ **Step 4:** Is this a **Full Day** or **Half Day**?"

#     # ============================================================
#     # STEP 5: REASON
#     # ============================================================
#     elif leave_draft["step"] == "duration":
#         selected = message.lower().strip()
#         if selected not in ["full day", "half day", "full", "half"]:
#             response = "⚠️ Please choose: **Full Day** or **Half Day**."
#         else:
#             duration_val = "half day" if "half" in selected else "full day"
            
#             if duration_val == "half day" and leave_draft["start_date"] != leave_draft["end_date"]:
#                 response = f"❌ **Error:** Half Day requires Start Date and End Date to be the same.\nType **'Full Day'** or **'Exit'**."
#             else:
#                 # Balance Check
#                 days_cost = calculate_days(leave_draft["start_date"], leave_draft["end_date"], duration_val)
#                 can_proceed = True
#                 if leave_draft["type"] == "emergency":
#                     if employee.used_emergency_leaves + days_cost > 1.0:
#                         can_proceed = False
#                         response = f"❌ **Insufficient Balance:** You have {1-employee.used_emergency_leaves} Emergency leaves left."

#                 if can_proceed:
#                     leave_draft["duration"] = duration_val
#                     leave_draft["step"] = "reason"
#                     response = "📝 **Step 5:** What is the **reason** for your leave?"

#     # ============================================================
#     # STEP 6: COMPOSE METHOD
#     # ============================================================
#     elif leave_draft["step"] == "reason":
#         if len(message) < 4:
#             response = "⚠️ Reason too short. Please provide details."
#         else:
#             leave_draft["reason"] = message
#             leave_draft["step"] = "compose_mode"
#             response = "✍️ **Step 6:** Do you want to **Compose** the email yourself, or use **AI**?\n(Type **'Me'** or **'AI'**)"

#     # ============================================================
#     # STEP 7: DRAFTING (FIXED LOGIC)
#     # ============================================================
#     elif leave_draft["step"] == "compose_mode":
#         mode = message.lower()
        
#         # A. AI GENERATION
#         if any(x in mode for x in ["ai", "auto", "generate"]):
#             leave_draft["compose_mode"] = "ai"
#             prompt = (
#                 f"Write a leave request email for {user_name} to the Admin. "
#                 f"Type: {leave_draft['type']}, Duration: {leave_draft['duration']}. "
#                 f"Dates: {leave_draft['start_date']} to {leave_draft['end_date']}. "
#                 f"Reason: {leave_draft['reason']}. Keep it professional."
#             )
#             generated_body = llm.invoke(prompt).content.strip()
#             leave_draft["email_body"] = generated_body
            
#             # FIX: MOVE STEP FORWARD to 'review_draft' so we don't loop back here
#             leave_draft["step"] = "review_draft" 
#             response = f"📝 **AI Draft:**\n\n```text\n{generated_body}\n```\n\n**Step 7:** Any changes? (Type changes or 'No')"

#         # B. MANUAL INPUT
#         elif any(x in mode for x in ["me", "self", "custom"]):
#             leave_draft["compose_mode"] = "custom"
#             leave_draft["step"] = "writing_custom" # Move to writing state
#             response = "⌨️ Okay, please **type your email body** below:"
#         else:
#             response = "⚠️ Please type **'Me'** or **'AI'**."

#     # --- Catch Custom Writing Input ---
#     elif leave_draft["step"] == "writing_custom":
#         leave_draft["email_body"] = message
#         leave_draft["step"] = "review_draft" # Move to review
#         response = f"📝 **Draft Saved.**\n\n**Step 7:** Any changes? (Type changes or 'No')"

#     # ============================================================
#     # STEP 8: REVIEW & MODIFICATIONS
#     # ============================================================
#     elif leave_draft["step"] == "review_draft":
        
#         if message.lower() in ["no", "none", "ok", "next", "good", "looks good"]:
#             leave_draft["step"] = "ask_cc"
            
#             # Create Preview for CHAT ONLY (Not for Email)
#             final_email_preview = (
#                 f"Subject: Leave Request - {leave_draft['reason']}\n"
#                 f"To: {ADMIN_EMAIL}\n"
#                 f"----------------------------------------\n"
#                 f"{leave_draft['email_body']}\n\n"
#             )
#             # Store just for Step 9 display if needed, but we won't send it.
#             leave_draft["final_preview"] = final_email_preview 

#             response = f"""
# 📩 **Final Preview:**
# {final_email_preview}

# 👥 **Step 8: Notify Teammates (CC)**
# Who else should be notified? (Team Lead, Teammates?)
# *Enter email addresses separated by commas, or type **'None'**.*
# """
#         else:
#             # Handle Edits (AI Rewrite)
#             current = leave_draft["email_body"]
#             prompt = f"Rewrite email: '{current}'. Change request: '{message}'. Return only updated body."
#             new_body = llm.invoke(prompt).content.strip()
#             leave_draft["email_body"] = new_body
#             response = f"🔄 **Updated Draft:**\n\n```text\n{new_body}\n```\n\nAny other changes? (Type changes or **'No'**)"

#     # ============================================================
#     # STEP 9: SEND (CC HANDLING)
#     # ============================================================
#     elif leave_draft["step"] == "ask_cc":
        
#         # 1. Parse CCs
#         cc_list = []
#         if "none" not in message.lower() and "no" not in message.lower():
#             raw_ccs = message.replace(" ", "").split(",")
#             cc_list = [email for email in raw_ccs if "@" in email]

#         # 2. Update DB Balance
#         days = calculate_days(leave_draft["start_date"], leave_draft["end_date"], leave_draft["duration"])
#         if leave_draft["type"] == "emergency": 
#             employee.used_emergency_leaves += days
        
#         # 3. Save Request
#         new_req = LeaveRequest(
#             employee_id=employee.id,
#             reason=leave_draft["reason"],
#             start_date=datetime.strptime(leave_draft["start_date"], "%Y-%m-%d"),
#             end_date=datetime.strptime(leave_draft["end_date"], "%Y-%m-%d"),
#             type=leave_draft["type"], 
#             status="pending_approval"
#         )
#         db.add(new_req)
#         db.commit()

#         # 4. Send Email
#         final_body = (
#             f"{leave_draft['email_body']}\n\n"
#             f"--------------------------------\n"
#             f"🔴 Admin Action Required: Login to Portal to Approve/Reject."
#         )
        
#         try:
#             send_email(
#                 to_email=ADMIN_EMAIL, 
#                 subject=f"Leave Request: {user_name} ({leave_draft['type']})", 
#                 body=final_body,
#                 cc_emails=cc_list
#             )
            
#             cc_msg = f" (CC: {', '.join(cc_list)})" if cc_list else ""
#             response = f"✅ **Request Sent!**\n\n📩 Sent to Admin{cc_msg}.\n📅 Status: Pending Approval."
#             state["notification"] = "🚀 Leave Applied Successfully!"
        
#         except Exception as e:
#             response = f"⚠️ Request saved to DB, but Email failed: {e}"
        
#         leave_draft = {} # Reset Draft

#     return {
#         **state, 
#         "leave_draft": leave_draft, 
#         "messages": state["messages"] + [{"role": "assistant", "content": response}]
#     }



"""
leave_node.py
"""
from models import LeaveRequest, Employee
from datetime import datetime
from email_service import send_email
import re
import os

APP_LINK = "https://hrmsagent.streamlit.app/" 
# Recommendation: Send to your personal email to verify it works
ADMIN_EMAIL = "bharathkumarking143@gmail.com" 

def is_valid_date(date_str):
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", date_str.strip()))

def calculate_days(start_str, end_str, duration_type):
    s = datetime.strptime(start_str, "%Y-%m-%d")
    e = datetime.strptime(end_str, "%Y-%m-%d")
    days = (e - s).days + 1
    if duration_type == "half day":
        return 0.5
    return float(days)

def leave_node(state):
    db = state["db"]
    message = state.get("message", "").strip()
    user_email = state["user_id"]
    llm = state.get("llm")
    
    employee = db.query(Employee).filter(Employee.email == user_email).first()
    user_name = employee.name if employee and employee.name else "Employee"
    leave_draft = state.get("leave_draft") or {}
    response = ""

    # --- 0. CANCEL COMMAND ---
    cancel_triggers = ["cancel", "stop", "abort", "exit", "quit", "end"]
    if any(x in message.lower() for x in cancel_triggers):
        return {
            **state, 
            "leave_draft": {}, 
            "messages": state["messages"] + [{"role": "assistant", "content": "❌ **Process Stopped.** Request cancelled."}]
        }

    # STEP 1: START DATE
    if not leave_draft.get("step"):
        leave_draft["step"] = "start_date"
        response = "📅 **Step 1:** What is the **Start Date**? (YYYY-MM-DD)"

    # STEP 2: END DATE
    elif leave_draft["step"] == "start_date":
        if is_valid_date(message):
            leave_draft["start_date"] = message
            leave_draft["step"] = "end_date"
            response = "📅 **Step 2:** What is the **End Date**? (YYYY-MM-DD)"
        else:
            response = "⚠️ Invalid format. Please use **YYYY-MM-DD** (e.g., 2025-02-20)."

    # STEP 3: LEAVE TYPE
    elif leave_draft["step"] == "end_date":
        if is_valid_date(message):
            if message < leave_draft["start_date"]:
                response = "⚠️ **Error:** End date cannot be before Start date."
            else:
                leave_draft["end_date"] = message
                leave_draft["step"] = "type"
                response = "📋 **Step 3:** What type of leave is this?\n(Options: **Emergency** or **Unpaid**)"
        else:
            response = "⚠️ Invalid format. Please use **YYYY-MM-DD**."

    # STEP 4: DURATION
    elif leave_draft["step"] == "type":
        selected = message.lower().strip()
        if selected not in ["unpaid", "emergency"]:
            response = "⚠️ Invalid type. Please choose: **Emergency** or **Unpaid**."
        else:
            leave_draft["type"] = selected
            leave_draft["step"] = "duration"
            response = "⏳ **Step 4:** Is this a **Full Day** or **Half Day**?"

    # STEP 5: REASON
    elif leave_draft["step"] == "duration":
        selected = message.lower().strip()
        if selected not in ["full day", "half day", "full", "half"]:
            response = "⚠️ Please choose: **Full Day** or **Half Day**."
        else:
            duration_val = "half day" if "half" in selected else "full day"
            if duration_val == "half day" and leave_draft["start_date"] != leave_draft["end_date"]:
                response = f"❌ **Error:** Half Day requires Start Date and End Date to be the same.\nType **'Full Day'** or **'Exit'**."
            else:
                days_cost = calculate_days(leave_draft["start_date"], leave_draft["end_date"], duration_val)
                can_proceed = True
                if leave_draft["type"] == "emergency":
                    if employee.used_emergency_leaves + days_cost > 1.0:
                        can_proceed = False
                        response = f"❌ **Insufficient Balance:** You have {1-employee.used_emergency_leaves} Emergency leaves left."

                if can_proceed:
                    leave_draft["duration"] = duration_val
                    leave_draft["step"] = "reason"
                    response = "📝 **Step 5:** What is the **reason** for your leave?"

    # STEP 6: COMPOSE METHOD
    elif leave_draft["step"] == "reason":
        if len(message) < 4:
            response = "⚠️ Reason too short. Please provide details."
        else:
            leave_draft["reason"] = message
            leave_draft["step"] = "compose_mode"
            response = "✍️ **Step 6:** Do you want to **Compose** the email yourself, or use **AI**?\n(Type **'Me'** or **'AI'**)"

    # STEP 7: DRAFTING
    elif leave_draft["step"] == "compose_mode":
        mode = message.lower()
        if any(x in mode for x in ["ai", "auto", "generate"]):
            leave_draft["compose_mode"] = "ai"
            prompt = (
                f"Write a leave request email for {user_name} to the Admin. "
                f"Type: {leave_draft['type']}, Duration: {leave_draft['duration']}. "
                f"Dates: {leave_draft['start_date']} to {leave_draft['end_date']}. "
                f"Reason: {leave_draft['reason']}. Keep it professional."
            )
            try:
                generated_body = llm.invoke(prompt).content.strip()
            except:
                generated_body = f"Dear Admin,\n\nI request {leave_draft['type']} leave from {leave_draft['start_date']} to {leave_draft['end_date']} due to {leave_draft['reason']}."
            
            leave_draft["email_body"] = generated_body
            leave_draft["step"] = "review_draft" 
            response = f"📝 **AI Draft:**\n\n```text\n{generated_body}\n```\n\n**Step 7:** Any changes? (Type changes or 'No')"

        elif any(x in mode for x in ["me", "self", "custom"]):
            leave_draft["compose_mode"] = "custom"
            leave_draft["step"] = "writing_custom" 
            response = "⌨️ Okay, please **type your email body** below:"
        else:
            response = "⚠️ Please type **'Me'** or **'AI'**."

    elif leave_draft["step"] == "writing_custom":
        leave_draft["email_body"] = message
        leave_draft["step"] = "review_draft" 
        response = f"📝 **Draft Saved.**\n\n**Step 7:** Any changes? (Type changes or 'No')"

    # STEP 8: REVIEW
    elif leave_draft["step"] == "review_draft":
        if message.lower() in ["no", "none", "ok", "next", "good", "looks good"]:
            leave_draft["step"] = "ask_cc"
            final_email_preview = f"Subject: Leave Request - {leave_draft['reason']}\nTo: {ADMIN_EMAIL}\n----------------------------------------\n{leave_draft['email_body']}\n\n"
            leave_draft["final_preview"] = final_email_preview 
            response = f"""📩 **Final Preview:**\n{final_email_preview}\n👥 **Step 8: Notify Teammates (CC)**\nWho else should be notified? (Team Lead, Teammates?)\n*Enter emails separated by commas, or type **'None'**.*"""
        else:
            current = leave_draft["email_body"]
            prompt = f"Rewrite email: '{current}'. Change request: '{message}'. Return only updated body."
            try:
                new_body = llm.invoke(prompt).content.strip()
            except:
                new_body = message
            leave_draft["email_body"] = new_body
            response = f"🔄 **Updated Draft:**\n\n```text\n{new_body}\n```\n\nAny other changes? (Type changes or **'No'**)"

    # STEP 9: SEND (CC HANDLING)
    elif leave_draft["step"] == "ask_cc":
        cc_list = []
        if "none" not in message.lower() and "no" not in message.lower():
            raw_ccs = message.replace(" ", "").split(",")
            cc_list = [email for email in raw_ccs if "@" in email]

        days = calculate_days(leave_draft["start_date"], leave_draft["end_date"], leave_draft["duration"])
        if leave_draft["type"] == "emergency": 
            employee.used_emergency_leaves += days
        
        new_req = LeaveRequest(
            employee_id=employee.id,
            reason=leave_draft["reason"],
            start_date=datetime.strptime(leave_draft["start_date"], "%Y-%m-%d"),
            end_date=datetime.strptime(leave_draft["end_date"], "%Y-%m-%d"),
            leave_type=leave_draft["type"], 
            status="pending_approval"
        )
        db.add(new_req)
        db.commit()

        # Send Email
        final_body = f"{leave_draft['email_body']}\n\n--------------------------------\n🔴 Admin Action Required: Login to Portal to Approve/Reject.\n link: https://hrmsagent.streamlit.app/"
        
        # 👇 FIX: Check Return Value directly!
        email_success = send_email(
            to_email=ADMIN_EMAIL, 
            subject=f"Leave Request: {user_name} ({leave_draft['type']})", 
            body=final_body,
            cc_emails=cc_list
        )

        cc_msg = f" (CC: {', '.join(cc_list)})" if cc_list else ""
        
        if email_success:
             response = f"✅ **Request Sent!**\n\n📩 Sent to Admin{cc_msg}.\n📅 Status: Pending Approval."
             state["notification"] = "🚀 Leave Applied Successfully!"
        else:
             response = f"⚠️ **Request Saved**, but Email Failed.\n(Admin can still see it on the Dashboard)."
        
        leave_draft = {} 

    return {
        **state, 
        "leave_draft": leave_draft, 
        "messages": state["messages"] + [{"role": "assistant", "content": response}]
    }