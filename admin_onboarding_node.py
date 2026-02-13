# """
# admin_onboarding_node.py
# """
# from models import Employee, Onboarding, LeaveRequest
# from email_service import send_email

# def admin_onboarding_node(state):
#     db = state["db"]
#     message = state.get("message", "").lower()

#     if "messages" not in state:
#         state["messages"] = []

#     # -----------------------------
#     # 1. ADMIN DASHBOARD / PENDING SUMMARY
#     # -----------------------------
#     if any(k in message for k in ["pending", "requests", "status", "show"]):
#         p_onboard = db.query(Employee).filter(
#             Employee.onboarding_status == "pending_approval"
#         ).count()

#         p_leave = db.query(LeaveRequest).filter(
#             LeaveRequest.status == "pending_approval"
#         ).count()

#         state["messages"].append({
#             "role": "assistant",
#             "content": (
#                 "📋 **Current Pending Requests:**\n\n"
#                 f"• Onboarding: {p_onboard}\n"
#                 f"• Leave Requests: {p_leave}\n\n"
#                 "Type **'check onboarding'** or **'check leaves'**."
#             )
#         })
#         return state

#     # -----------------------------
#     # 2. FIND PENDING ONBOARDINGS
#     # -----------------------------
#     pending_employees = db.query(Employee).filter(
#         Employee.onboarding_status == "pending_approval"
#     ).all()

#     if not pending_employees:
#         state["messages"].append({
#             "role": "assistant",
#             "content": "✅ No pending onboarding requests found."
#         })
#         return state

#     # -----------------------------
#     # 3. APPROVE ALL
#     # -----------------------------
#     if "approve" in message:
#         approved = []

#         for emp in pending_employees:
#             emp.onboarding_status = "completed"
#             approved.append(emp.name)

#             target_email = emp.personal_email or emp.email
#             send_email(
#                 target_email,
#                 "Onboarding Approved - Welcome!",
#                 f"Dear {emp.name},\n\nYour onboarding has been approved.\n\nWelcome aboard!"
#             )

#         db.commit()

#         state["messages"].append({
#             "role": "assistant",
#             "content": f"✅ **Approved:** {', '.join(approved)}"
#         })
#         return state

#     # -----------------------------
#     # 4. LIST PENDING DETAILS
#     # -----------------------------
#     msg = "**Pending Onboarding Requests:**\n"
#     for emp in pending_employees:
#         onboarding = db.query(Onboarding).filter(
#             Onboarding.employee_id == emp.id
#         ).first()
#         details = onboarding.data.replace("\n", ", ") if onboarding else "No data"
#         msg += f"- **{emp.name}** ({emp.personal_email}): {details[:100]}...\n"

#     msg += "\nType **'approve onboarding'** to approve all."
#     state["messages"].append({"role": "assistant", "content": msg})

#     return state


"""
admin_onboarding_node.py
"""
# from models import Employee, Onboarding, LeaveRequest
# from email_service import send_email

# def admin_onboarding_node(state):
#     db = state["db"]
#     message = state.get("message", "").lower()
#     if "messages" not in state: state["messages"] = []

#     # 1. DASHBOARD
#     if any(k in message for k in ["pending", "requests", "status", "show"]):
#         p_onboard = db.query(Employee).filter(Employee.onboarding_status == "pending_approval").count()
#         p_leave = db.query(LeaveRequest).filter(LeaveRequest.status == "pending_approval").count()
#         state["messages"].append({"role": "assistant", "content": f"📋 **Current Pending Requests:**\n\n• Onboarding: {p_onboard}\n• Leave Requests: {p_leave}\n\nType **'check onboarding'** or **'check leaves'**."})
#         return state

#     # 2. FIND PENDING
#     pending_employees = db.query(Employee).filter(Employee.onboarding_status == "pending_approval").all()
#     if not pending_employees:
#         state["messages"].append({"role": "assistant", "content": "✅ No pending onboarding requests found."})
#         return state

#     # 3. APPROVE ALL
#     if "approve" in message:
#         approved = []
#         for emp in pending_employees:
#             emp.onboarding_status = "completed"
#             approved.append(emp.name)
#             target_email = emp.personal_email or emp.email
#             send_email(target_email, "Onboarding Approved - Welcome!", f"Dear {emp.name},\n\nYour onboarding has been approved.\n\nWelcome aboard!")

#         db.commit()
        
#         # --- NOTIFICATION ---
#         state["notification"] = f"✅ Approved {len(approved)} Onboarding Requests!"
#         # --------------------
        
#         state["messages"].append({"role": "assistant", "content": f"✅ **Approved:** {', '.join(approved)}"})
#         return state

#     # 4. LIST PENDING
#     msg = "**Pending Onboarding Requests:**\n"
#     for emp in pending_employees:
#         onboarding = db.query(Onboarding).filter(Onboarding.employee_id == emp.id).first()
#         details = onboarding.data.replace("\n", ", ") if onboarding else "No data"
#         msg += f"- **{emp.name}** ({emp.personal_email}): {details[:100]}...\n"
#     msg += "\nType **'approve onboarding'** to approve all."
#     state["messages"].append({"role": "assistant", "content": msg})
#     return state


# """
# admin_onboarding_node.py
# """
# from models import Employee, Onboarding
# from email_service import send_email
# import random
# from datetime import datetime

# def extract_name(message, triggers):
#     """Helper to extract name robustly"""
#     # 1. Sort triggers by length (Longest first) to avoid partial cuts
#     # This prevents "onboarding" becoming "ing" when "onboard" is removed
#     sorted_triggers = sorted(triggers, key=len, reverse=True)
    
#     for t in sorted_triggers:
#         message = message.replace(t, "")
    
#     # 2. Remove common prepositions
#     message = message.replace(" for ", " ").replace(" of ", " ").replace(" to ", " ").replace(" about ", " ")
    
#     return message.strip()

# def get_joined_date(user):
#     """Safely get date string"""
#     if hasattr(user, 'created_at') and user.created_at:
#         return user.created_at.strftime('%Y-%m-%d')
#     return "Recent"

# def admin_onboarding_node(state):
#     db = state["db"]
#     message = state.get("message", "").lower()
#     if "messages" not in state: state["messages"] = []

#     # =========================================================
#     # 1. SHOW LISTS (STRICTLY SEPARATED)
#     # =========================================================
    
#     # A. SHOW ACTIVE EMPLOYEES ONLY
#     # Added "all employees", "show all" to catch variations
#     if any(x in message for x in ["show employees", "list employees", "active employees", "staff", "all employees", "show all", "list all"]):
#         # STRICT FILTER: Only 'active' status
#         active_emps = db.query(Employee).filter(Employee.onboarding_status == "active").all()
        
#         if not active_emps:
#             state["messages"].append({"role": "assistant", "content": "ℹ️ No active employees found."})
#         else:
#             msg = "### 🏢 Active Employee Directory\n| Name | ID | Role | Email |\n|---|---|---|---|\n"
#             for e in active_emps:
#                 msg += f"| {e.name} | `{e.employee_id_str}` | {e.role} | {e.email} |\n"
#             state["messages"].append({"role": "assistant", "content": msg})
#         return state

#     # B. SHOW NEW JOINERS ONLY
#     if any(x in message for x in ["show new", "new joiner", "onboarding list", "pending", "candidates"]):
#         joiners = db.query(Employee).filter(Employee.onboarding_status != "active").all()
        
#         if not joiners:
#             state["messages"].append({"role": "assistant", "content": "✅ No new joiners pending."})
#         else:
#             msg = "### ⏳ New Joiner Candidates\n| Name | Email | Current Step |\n|---|---|---|\n"
#             for j in joiners:
#                 step_icon = "📝 Signed Up" if j.onboarding_status == "signed_up" else "📩 Invited" if j.onboarding_status == "onboarding_triggered" else "✅ Ready"
#                 msg += f"| {j.name} | {j.email} | {step_icon} |\n"
            
#             msg += "\n**Actions:**\n- `Start onboarding [name]`\n- `Remind [name]`\n- `Finalize [name]`"
#             state["messages"].append({"role": "assistant", "content": msg})
#         return state

#     # =========================================================
#     # 2. SEARCH DETAILS
#     # =========================================================
#     if any(x in message for x in ["show", "search", "find", "profile", "details"]) and any(x in message for x in ["details", "info", "employee", "id", "joiner", "candidate"]):
#         name_target = extract_name(message, ["show", "search", "details", "employee", "profile", "info", "find", "me", "the", "joiner", "candidate"])
#         if len(name_target) < 2:
#             state["messages"].append({"role": "assistant", "content": "⚠️ Specify name. Example: **'Show details for Bharath'**"})
#             return state

#         user = db.query(Employee).filter(Employee.name.ilike(f"%{name_target}%")).first()
        
#         if user:
#             # VIEW 1: ACTIVE EMPLOYEE
#             if user.onboarding_status == "active":
#                 e_left = max(0, 1 - user.used_emergency_leaves)
#                 msg = f"""
# ### 🆔 Employee Profile: {user.name}
# _(Active Staff)_

# | **Category** | **Details** |
# | :--- | :--- |
# | **📧 Email** | {user.email} |
# | **🆔 Emp ID** | `{user.employee_id_str}` |
# | **💼 Role** | {user.role.title()} |
# | **🚑 Emergency** | **{e_left}** / 1 |

# _Joined: {get_joined_date(user)}_
# """
#                 state["messages"].append({"role": "assistant", "content": msg})

#             # VIEW 2: NEW JOINER
#             else:
#                 onboard_data = db.query(Onboarding).filter(Onboarding.employee_id == user.id).first()
#                 formatted_data = ""
#                 if onboard_data and onboard_data.data:
#                     raw_lines = onboard_data.data.strip().split('\n')
#                     for line in raw_lines:
#                         if "Final Employee ID" in line: continue 
#                         if ":" in line:
#                             key, val = line.split(":", 1)
#                             formatted_data += f"- **{key.strip()}:** {val.strip()}\n"
#                         else:
#                             formatted_data += f"- {line}\n"
#                 else:
#                     formatted_data = "_No details submitted yet._"

#                 msg = f"""
# ### 📋 Candidate Profile: {user.name}
# _(New Joiner - {user.onboarding_status.upper()})_

# | **Category** | **Details** |
# | :--- | :--- |
# | **📧 Email** | {user.email} |
# | **📅 Joined System** | {get_joined_date(user)} |
# | **⚠️ Action** | _Pending Onboarding_ |

# #### 📝 Submitted Form Data
# {formatted_data}
# """
#                 state["messages"].append({"role": "assistant", "content": msg})
#         else:
#             state["messages"].append({"role": "assistant", "content": f"❌ No user found matching '{name_target}'."})
#         return state

#     # =========================================================
#     # 3. ACTION: TRIGGER ONBOARDING
#     # =========================================================
#     if "start onboarding" in message:
#         # Added "start" to triggers to ensure clean extraction
#         name_target = extract_name(message, ["start onboarding", "start", "invite"])
#         user = db.query(Employee).filter(Employee.name.ilike(f"%{name_target}%"), Employee.onboarding_status == "signed_up").first()
#         if user:
#             user.onboarding_status = "onboarding_triggered"
#             db.commit()
#             send_email(user.email, "Action Required", f"Welcome {user.name}! Login to fill details: http://localhost:8501")
#             state["notification"] = f"📧 Invite sent to {user.name}"
#             state["messages"].append({"role": "assistant", "content": f"✅ Invite sent to {user.name}."})
#         else:
#             state["messages"].append({"role": "assistant", "content": f"⚠️ Candidate '{name_target}' not found (or already invited)."})
#         return state

#     # =========================================================
#     # 4. ACTION: REJECT & RESET
#     # =========================================================
#     if "reject" in message:
#         name_target = extract_name(message, ["reject onboarding", "reject"])
#         user = db.query(Employee).filter(Employee.name.ilike(f"%{name_target}%")).first()
        
#         if user and user.onboarding_status != "active":
#             user.onboarding_status = "onboarding_triggered"
#             onboarding = db.query(Onboarding).filter(Onboarding.employee_id == user.id).first()
#             if onboarding:
#                 onboarding.step = 1
#                 onboarding.completed = False
#                 onboarding.data = "" 
#             db.commit()
#             send_email(user.email, "Onboarding Rejected", f"Dear {user.name},\nPlease login and fill your details again.")
#             state["notification"] = f"🚫 Reset {user.name}"
#             state["messages"].append({"role": "assistant", "content": f"✅ **Rejected & Reset:** {user.name}."})
#         else:
#              state["messages"].append({"role": "assistant", "content": f"⚠️ Cannot reject '{name_target}'."})
#         return state

#     # =========================================================
#     # 5. ACTION: SEND REMINDER
#     # =========================================================
#     if "remind" in message or "send reminder" in message:
#         name_target = extract_name(message, ["remind", "send reminder", "mail", "email", "to"])
        
#         user = db.query(Employee).filter(
#             Employee.name.ilike(f"%{name_target}%"), 
#             Employee.onboarding_status == "onboarding_triggered"
#         ).first()

#         if user:
#             subject = "Reminder: Complete Your Onboarding"
#             body = f"Dear {user.name},\n\nThis is a gentle reminder to complete your onboarding details.\nPlease login here: http://localhost:8501"
            
#             send_email(user.email, subject, body)
#             state["notification"] = f"🔔 Reminder sent to {user.name}"
#             state["messages"].append({"role": "assistant", "content": f"✅ **Reminder Sent:** Email dispatched to {user.name}."})
#         else:
#             state["messages"].append({"role": "assistant", "content": f"⚠️ User '{name_target}' is not pending (or not found)."})
#         return state

#     # =========================================================
#     # 6. ACTION: CHECK STATUS / DASHBOARD
#     # =========================================================
#     if "filled" in message or "check onboarding" in message or "status" in message:
#         # List A: Ready for Admin
#         filled = db.query(Employee).filter(Employee.onboarding_status == "details_submitted").all()
#         # List B: Waiting for Candidate
#         pending = db.query(Employee).filter(Employee.onboarding_status == "onboarding_triggered").all()
        
#         msg = "📊 **Onboarding Status Report:**\n\n"
        
#         if filled:
#             msg += "**✅ Details Filled (Ready to Finalize):**\n"
#             for f in filled: msg += f"- {f.name} (Type: 'Finalize {f.name}')\n"
#         else:
#             msg += "**✅ Details Filled:** None\n"
            
#         if pending:
#             msg += "\n**⏳ Waiting for Candidate (Send Reminder):**\n"
#             for p in pending: msg += f"- {p.name} (Type: 'Remind {p.name}')\n"
#         else:
#             msg += "\n**⏳ Waiting for Candidate:** None\n"

#         state["messages"].append({"role": "assistant", "content": msg})
#         return state

#     # =========================================================
#     # 7. ACTION: FINALIZE (UPDATED)
#     # =========================================================
#     if "finalize" in message or "offer" in message:
#         # Added 'onboarding' (without 'onboard') to logic or just ensure sorted triggers handle it
#         name_target = extract_name(message, ["finalize onboarding", "finalize", "onboard", "offer"])
#         user = db.query(Employee).filter(Employee.name.ilike(f"%{name_target}%"), Employee.onboarding_status == "details_submitted").first()
        
#         if user:
#             new_emp_id = f"EMP{random.randint(1000,9999)}"
#             user.employee_id_str = new_emp_id
#             user.onboarding_status = "active"
            
#             onboard_record = db.query(Onboarding).filter(Onboarding.employee_id == user.id).first()
#             if onboard_record:
#                 onboard_record.data += f"\nFinal Employee ID: {new_emp_id}"
#                 onboard_record.completed = True

#             db.commit()
            
#             # EMAIL 1: WELCOME & OFFER (HR Team)
#             welcome_subject = f"Welcome to the Team! - {user.name}"
#             welcome_body = f"""
# Dear {user.name},

# We are thrilled to formally welcome you to Your Volta Services Pvt Ltd!

# Here are your official employment details:
# --------------------------------------------------
# 🆔 Employee ID : {new_emp_id}
# 📧 Email       : {user.email}
# 🚀 Status      : Active
# --------------------------------------------------

# Your onboarding is now complete. You can now access all employee portals.

# Best Regards,
# HR Team
# """
#             send_email(user.email, welcome_subject, welcome_body)
            
#             # EMAIL 2: IT ASSET DISPATCH (Network Team)
#             asset_subject = f"IT Asset Dispatch Details - {user.name}"
#             asset_body = f"""
# Dear {user.name},

# This email is to confirm that your IT assets have been configured and dispatched by the Network Team.

# 📦 Asset Details:
# - Device: MacBook Pro M3 (16GB/512GB)
# - Serial No: #Apple-{random.randint(10000,99999)}
# - Accessories: Charger, Magic Mouse, Laptop Sleeve

# 🚚 Tracking ID: #TRK-{random.randint(88888,99999)} (BlueDart)

# Please verify the contents upon delivery and report any issues to IT immediately.

# Regards,
# Network & IT Operations Team
# """
#             send_email(user.email, asset_subject, asset_body)

#             state["notification"] = f"🚀 {user.name} Active!"
#             state["messages"].append({"role": "assistant", "content": f"✅ **Success!** {user.name} is now Active.\n\n📧 **Emails Sent:**\n1. Welcome Letter (HR)\n2. Asset Dispatch (IT Team)"})
#         else:
#             state["messages"].append({"role": "assistant", "content": f"⚠️ User '{name_target}' is not ready to finalize."})
#         return state

#     state["messages"].append({"role": "assistant", "content": "I can help. Try:\n- 'Show active employees'\n- 'Show new joiners'\n- 'Check onboarding status'\n- 'Remind [name]'\n- 'Finalize [name]'"})
#     return state



"""
admin_onboarding_node.py
"""
from models import Employee, Onboarding, LeaveRequest
from email_service import send_email
import random
from datetime import datetime

def extract_name(message, triggers):
    sorted_triggers = sorted(triggers, key=len, reverse=True)
    for t in sorted_triggers: message = message.replace(t, "")
    return message.replace(" for ", " ").replace(" of ", " ").replace(" about ", " ").strip()

def admin_onboarding_node(state):
    db = state["db"]
    message = state.get("message", "").lower().strip()
    if "messages" not in state: state["messages"] = []

    # =========================================================
    # 1. SPECIFIC DASHBOARD: LEAVES
    # =========================================================
    if "leave" in message and ("show" in message or "requests" in message or "list" in message):
        leaves = db.query(LeaveRequest).filter(LeaveRequest.status == "pending_approval").all()
        
        if not leaves:
            state["messages"].append({"role": "assistant", "content": "✅ No pending leave requests."})
        else:
            msg = "### 🏖️ Pending Leave Requests\n| Employee | Date(s) | Type | Days |\n|---|---|---|---|\n"
            for l in leaves:
                emp = db.query(Employee).filter(Employee.id == l.employee_id).first()
                name = emp.name if emp else "Unknown"
                days = (l.end_date - l.start_date).days + 1
                l_type = getattr(l, "leave_type", "Unknown") 
                msg += f"| **{name}** | {l.start_date.strftime('%Y-%m-%d')} | {l_type.title()} | {days} |\n"
            
            msg += "\n**Actions:**\n- `Approve leave for [Name]`\n- `Reject leave for [Name]`\n- `Approve leaves for all`"
            state["messages"].append({"role": "assistant", "content": msg})
        return state

    # =========================================================
    # 2. SPECIFIC DASHBOARD: ONBOARDING
    # =========================================================
    if "onboarding" in message and ("show" in message or "requests" in message or "list" in message):
        candidates = db.query(Employee).filter(Employee.onboarding_status != "active").all()
        
        if not candidates:
            state["messages"].append({"role": "assistant", "content": "✅ No onboarding requests pending."})
        else:
            submitted = []
            pending = []
            
            for c in candidates:
                if c.onboarding_status == "details_submitted":
                    submitted.append(c.name)
                else:
                    pending.append(c.name)
            
            msg = "### ⏳ Onboarding Dashboard\n\n"
            
            if submitted:
                msg += "**✅ Details Submitted (Ready to Finalize):**\n"
                for name in submitted:
                    msg += f"- **{name}**\n"
            else:
                msg += "**✅ Details Submitted:** None\n"

            if pending:
                msg += "\n**⚠️ Pending Candidate Action (Need Reminder):**\n"
                for name in pending:
                    msg += f"- {name}\n"
            else:
                msg += "\n**⚠️ Pending Candidate Action:** None\n"

            msg += "\n**Actions:**\n- `Show details for [Name]`\n- `Finalize [Name]`\n- `Reject [Name]`\n- `Remind [Name]`"
            state["messages"].append({"role": "assistant", "content": msg})
        return state

    # =========================================================
    # 3. MAIN SUMMARY DASHBOARD (General)
    # =========================================================
    if any(x in message for x in ["pending", "dashboard", "requests", "updates", "status"]):
        joiners_count = db.query(Employee).filter(Employee.onboarding_status != "active").count()
        leaves_count = db.query(LeaveRequest).filter(LeaveRequest.status == "pending_approval").count()
        
        msg = f"""
📊 **Admin Dashboard Overview (v3)**

| Category | Pending Count | Command to View |
| :--- | :---: | :--- |
| **🏖️ Leaves** | **{leaves_count}** | Type **'Show leave requests'** |
| **⏳ Onboarding** | **{joiners_count}** | Type **'Show onboarding requests'** |

_Select a category above to take action._
"""
        state["messages"].append({"role": "assistant", "content": msg})
        return state

    # =========================================================
    # 4. SHOW LISTS (Active Directory)
    # =========================================================
    is_list_request = any(x in message for x in ["list", "directory", "all employees", "active employees", "show all"])
    
    if is_list_request:
        active_emps = db.query(Employee).filter(Employee.onboarding_status == "active").all()
        if not active_emps:
            state["messages"].append({"role": "assistant", "content": "ℹ️ No active employees found."})
        else:
            msg = "### 🏢 Active Employee Directory\n| Name | ID | Role | Email |\n|---|---|---|---|\n"
            for e in active_emps:
                msg += f"| {e.name} | `{e.employee_id_str}` | {e.role} | {e.email} |\n"
            state["messages"].append({"role": "assistant", "content": msg})
        return state

    # =========================================================
    # 5. START / CREATE ACTIONS
    # =========================================================
    is_start_cmd = False
    if "," not in message: 
        if message == "onboard":
            is_start_cmd = True
        elif "onboard" in message and any(k in message for k in ["start", "lets", "let's", "new", "begin"]):
            is_start_cmd = True

    if is_start_cmd:
        msg = "👋 **Sure!** To onboard a new user, please type:\n`Onboard Name, Email, Password`"
        state["messages"].append({"role": "assistant", "content": msg})
        return state

    if message.startswith("onboard ") and "," in message:
        try:
            parts = [p.strip() for p in message[8:].split(",")]
            if len(parts) != 3: raise ValueError
            
            name, email, password = parts[0], parts[1].lower(), parts[2]
            
            if db.query(Employee).filter(Employee.email == email).first():
                state["messages"].append({"role": "assistant", "content": f"⚠️ User {email} exists."})
                return state

            new_emp = Employee(name=name, email=email, password=password, role="employee", onboarding_status="onboarding_triggered")
            db.add(new_emp); db.commit()
            
            send_email(email, "Welcome to Volta!", f"Hi {name},\n\nYour account has been created.\n\nLogin: {email}\nPass: {password}\n\nPlease login to complete your onboarding. Here is the link https://hrmsagent.streamlit.app/")
            
            state["notification"] = f"✅ Created {name}"
            state["messages"].append({"role": "assistant", "content": f"✅ Created user **{name}**. Invitation email sent!"})
        except:
            state["messages"].append({"role": "assistant", "content": "⚠️ Format: `Onboard Name, Email, Password`"})
        return state

    # =========================================================
    # 6. SHOW SINGLE DETAILS (FIXED: Handles "Waiting" Status)
    # =========================================================
    if any(x in message for x in ["details", "profile", "info", "give", "show"]):
        name_target = extract_name(message, ["show", "give me", "give", "details", "profile", "info", "about"])
        
        if "all" in name_target:
             state["messages"].append({"role": "assistant", "content": "📋 Please use **'List all employees'** to see everyone."})
             return state

        user = db.query(Employee).filter(Employee.name.ilike(f"%{name_target}%")).first()
        
        if user:
            status_check = str(user.onboarding_status).strip().lower()

            # CASE A: Active Employee
            if status_check == "active":
                e_left = max(0, 1 - user.used_emergency_leaves)
                msg = f"""
### 👤 Profile: {user.name}
- **Email:** {user.email}
- **ID:** `{user.employee_id_str}`
- **Role:** {user.role}
- **Leaves:** Paid ({1-user.used_paid_leaves}), Emergency ({e_left})
"""
            # CASE B: Waiting for Candidate (This is the MISSING PART)
            elif status_check == "onboarding_triggered":
                 msg = (
                    f"👤 **Candidate:** {user.name}\n"
                    f"🔄 **Status:** Waiting for Candidate\n\n"
                    f"⚠️ **Note:** {user.name} has NOT submitted their form yet.\n"
                    f"You can type **'Remind {user.name}'** to send them an email."
                )

            # CASE C: Submitted Candidates
            else:
                onboard_rec = db.query(Onboarding).filter(Onboarding.employee_id == user.id).first()
                details = onboard_rec.data if onboard_rec else "No data found."
                msg = f"👤 **Candidate:** {user.name}\n**Status:** {user.onboarding_status}\n\n**Data:**\n{details}\n\n**Actions:**\n- `Finalize {user.name}`\n- `Reject {user.name}`"
                
            state["messages"].append({"role": "assistant", "content": msg})
        else:
            state["messages"].append({"role": "assistant", "content": f"❌ User **{name_target}** not found."})
        return state

    # =========================================================
    # 7. REMIND, FINALIZE & REJECT
    # =========================================================
    if "remind" in message:
        name_target = extract_name(message, ["remind", "send reminder", "reminder"])
        user = db.query(Employee).filter(Employee.name.ilike(f"%{name_target}%")).first()
        
        if user:
            if user.onboarding_status in ["onboarding_triggered", "details_submitted"]:
                send_email(user.email, "Action Required: Complete Onboarding", f"Hi {user.name},\n\nPlease login to complete your onboarding. click here https://hrmsagent.streamlit.app/")
                state["messages"].append({"role": "assistant", "content": f"✅ Reminder sent to **{user.name}**."})
            elif user.onboarding_status == "active":
                state["messages"].append({"role": "assistant", "content": f"ℹ️ {user.name} is already active."})
            else:
                 state["messages"].append({"role": "assistant", "content": f"ℹ️ {user.name} has status: {user.onboarding_status}."})
        else:
            state["messages"].append({"role": "assistant", "content": f"⚠️ User '{name_target}' not found."})
        return state

    if "finalize" in message:
        name_target = extract_name(message, ["finalize", "approve"])
        user = db.query(Employee).filter(Employee.name.ilike(f"%{name_target}%")).first()
        
        if user and user.onboarding_status == "details_submitted":
            new_id = f"EMP{random.randint(1000,9999)}"
            user.employee_id_str = new_id
            user.onboarding_status = "active"
            db.commit()
            send_email(user.email, f"Welcome to Volta! (ID: {new_id})", f"Hi {user.name},\n\nCongratulations! Your onboarding is complete.\nYour Employee ID is {new_id}.\n\nPlease login to the portal with your credentials https://hrmsagent.streamlit.app/.")
            state["messages"].append({"role": "assistant", "content": f"✅ **{user.name}** is now Active (ID: `{new_id}`).\n📧 Welcome email sent."})
        elif user:
             state["messages"].append({"role": "assistant", "content": f"⚠️ {user.name} is not ready (Status: {user.onboarding_status})."})
        else:
            state["messages"].append({"role": "assistant", "content": f"⚠️ User '{name_target}' not found."})
        return state

    if "reject" in message:
        name_target = extract_name(message, ["reject"])
        user = db.query(Employee).filter(Employee.name.ilike(f"%{name_target}%")).first()
        if user and user.onboarding_status == "details_submitted":
            user.onboarding_status = "onboarding_triggered"
            rec = db.query(Onboarding).filter(Onboarding.employee_id == user.id).first()
            if rec: rec.data = "" # Reset data
            db.commit()
            send_email(user.email, "Action Required", "Your submission was rejected. Please refill. link: https://hrmsagent.streamlit.app/")
            state["messages"].append({"role": "assistant", "content": f"❌ Rejected {user.name}. They must refill the form."})
        else:
            state["messages"].append({"role": "assistant", "content": "⚠️ User not in review status."})
        return state

    state["messages"].append({"role": "assistant", "content": "🤔 Try 'Show pending requests' or 'Help'."})
    return state