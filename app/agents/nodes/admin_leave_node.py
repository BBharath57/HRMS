# """
# admin_leave_node.py
# """
# from app.database.models import LeaveRequest, Employee
# from app.services.email_service import send_email
# from datetime import datetime

# def extract_name(message, triggers):
#     """Helper to extract name"""
#     for t in triggers:
#         message = message.replace(t, "")
#     message = message.replace("for", "").strip()
#     return message

# def admin_leave_node(state):
#     db = state["db"]
#     message = state.get("message", "").lower()
#     user_id = state["user_id"] 
#     if "messages" not in state: state["messages"] = []

#     pending_leaves = db.query(LeaveRequest).filter(LeaveRequest.status == "pending_approval").all()

#     # ---------------------------------------------------------
#     # 1. SHOW PENDING LEAVES
#     # ---------------------------------------------------------
#     if not pending_leaves:
#         state["messages"].append({"role": "assistant", "content": "✅ No pending leave requests."})
#         return state

#     # ---------------------------------------------------------
#     # 2. REJECT LEAVE (Manual)
#     # ---------------------------------------------------------
#     if "reject" in message:
#         name_target = extract_name(message, ["reject leave", "reject"])
        
#         target_leave = None
#         target_emp = None
        
#         for leave in pending_leaves:
#             emp = db.query(Employee).filter(Employee.id == leave.employee_id).first()
#             if emp and name_target in emp.name.lower():
#                 target_leave = leave
#                 target_emp = emp
#                 break
        
#         if target_leave and target_emp:
#             target_leave.status = "rejected"
#             target_leave.approved_by = None 
            
#             # REFUND BALANCE
#             days_cost = (target_leave.end_date - target_leave.start_date).days + 1
#             if "half" in (target_leave.reason or "").lower(): 
#                  days_cost = 0.5

#             if target_leave.leave_type == "emergency":
#                 target_emp.used_emergency_leaves -= days_cost
#                 if target_emp.used_emergency_leaves < 0: target_emp.used_emergency_leaves = 0
            
#             db.commit()
#             send_email(target_emp.email, "Leave Request Rejected", f"Dear {target_emp.name},\n\nYour leave request has been REJECTED by Admin.")
            
#             state["notification"] = f"🚫 Rejected leave for {target_emp.name}"
#             state["messages"].append({"role": "assistant", "content": f"✅ **Rejected:** Leave for {target_emp.name} has been cancelled and quota refunded."})
#         else:
#             state["messages"].append({"role": "assistant", "content": f"⚠️ Could not find a pending request for '{name_target}'."})
#         return state

#     # ---------------------------------------------------------
#     # 3. APPROVE LEAVE (Specific OR All)
#     # ---------------------------------------------------------
#     if "approve" in message:
#         admin_emp = db.query(Employee).filter(Employee.email == user_id).first()
#         admin_db_id = admin_emp.id if admin_emp else None
        
#         # --- NEW LOGIC: Check if specific name provided ---
#         name_target = extract_name(message, ["approve leave", "approve"])
        
#         target_list = []
        
#         # If user typed "Approve leave for Vamshi" (name length > 2)
#         if len(name_target) > 2:
#             found_specific = False
#             for leave in pending_leaves:
#                 emp = db.query(Employee).filter(Employee.id == leave.employee_id).first()
#                 if emp and name_target in emp.name.lower():
#                     target_list.append(leave)
#                     found_specific = True
            
#             if not found_specific:
#                 state["messages"].append({"role": "assistant", "content": f"⚠️ No pending leave found for '{name_target}'."})
#                 return state
#         else:
#             # If user just typed "Approve leaves", select ALL
#             target_list = pending_leaves

#         # Process the selected list
#         status_report = ""
#         for leave in target_list:
#             emp = db.query(Employee).filter(Employee.id == leave.employee_id).first()
#             if not emp: continue
            
#             target_email = emp.personal_email if emp.personal_email else emp.email
#             approved = False
#             reason = "Policy Violation"

#             # Check Limits
#             if leave.leave_type == "emergency":
#                 if emp.used_emergency_leaves <= 1.0: 
#                     approved = True
#                 else: 
#                     reason = "Emergency Quota Exceeded (Max 1)"
#             elif leave.leave_type == "unpaid":
#                 approved = True
#             else:
#                 reason = "Invalid Type"

#             if approved:
#                 leave.status = "approved"
#                 leave.approved_by = admin_db_id
#                 send_email(target_email, "Leave Request Approved", f"Dear {emp.name},\n\nYour {leave.leave_type} leave is APPROVED.")
#                 status_report += f"- ✅ Approved: {emp.name} ({leave.leave_type})\n"
#             else:
#                 leave.status = "rejected"
#                 # Refund logic
#                 days_cost = (leave.end_date - leave.start_date).days + 1
#                 if "half" in (leave.reason or "").lower(): days_cost = 0.5
#                 if leave.leave_type == "emergency": emp.used_emergency_leaves -= days_cost

#                 send_email(target_email, "Leave Request Rejected", f"Dear {emp.name},\n\nREJECTED: {reason}.")
#                 status_report += f"- ❌ Rejected: {emp.name} ({reason})\n"
        
#         db.commit()
#         state["notification"] = "✅ Requests Processed!"
#         state["messages"].append({"role": "assistant", "content": f"**Processed:**\n{status_report}"})
#         return state

#     # ---------------------------------------------------------
#     # 4. DASHBOARD (Default)
#     # ---------------------------------------------------------
#     msg = "**Pending Leave Requests:**\n"
#     for leave in pending_leaves:
#         emp = db.query(Employee).filter(Employee.id == leave.employee_id).first()
#         msg += f"- **{emp.name}**: {leave.leave_type.title()} ({leave.start_date.date()})\n"
#     msg += "\nCommands:\n- **'Approve leaves'** (Process ALL)\n- **'Approve leave for [name]'** (Process ONE)\n- **'Reject leave for [name]'**"
#     state["messages"].append({"role": "assistant", "content": msg})

#     return state




# render version

"""
admin_leave_node.py
"""
from app.database.models import LeaveRequest, Employee
from app.services.email_service import send_email
from datetime import datetime

def extract_name(message, triggers):
    """Helper to extract name"""
    for t in triggers:
        message = message.replace(t, "")
    message = message.replace("for", "").strip() #need to invitegate this more
    return message

def admin_leave_node(state):
    
    db = state["db"]
    message = state.get("message", "").lower()
    user_id = state["user_id"] 

    if "messages" not in state: state["messages"] = []

    pending_leaves = db.query(LeaveRequest).filter(LeaveRequest.status == "pending_approval").all()

    # 1. SHOW PENDING LEAVES
    if not pending_leaves and "approve" not in message and "reject" not in message:
        state["messages"].append({"role": "assistant", "content": "✅ No pending leave requests."})
        return state

    # 2. REJECT LEAVE (Manual)
    if "reject" in message:
        name_target = extract_name(message, ["reject leave", "reject"])
        
        target_leave = None
        target_emp = None
        
        for leave in pending_leaves:
            emp = db.query(Employee).filter(Employee.id == leave.employee_id).first()
            if emp and name_target in emp.name.lower():
                target_leave = leave
                target_emp = emp
                break
        
        if target_leave and target_emp:
            target_leave.status = "rejected"
            
            days_cost = (target_leave.end_date - target_leave.start_date).days + 1
            if "half" in (target_leave.reason or "").lower(): days_cost = 0.5

            if target_leave.leave_type == "emergency":
                target_emp.used_emergency_leaves -= days_cost
                if target_emp.used_emergency_leaves < 0: target_emp.used_emergency_leaves = 0
            
            db.commit()
            
            success = send_email(target_emp.email, "Leave Request Rejected", f"Dear {target_emp.name},\n\nYour leave request has been REJECTED by Admin.")
            
            email_status = "📧 Email Sent." if success else "⚠️ Email Failed (Check logs)."
            state["notification"] = f"🚫 Rejected leave for {target_emp.name}"
            state["messages"].append({"role": "assistant", "content": f"✅ **Rejected:** Leave for {target_emp.name} cancelled.\n{email_status}"})
        else:
            state["messages"].append({"role": "assistant", "content": f"⚠️ Could not find a pending request for '{name_target}'."})
        return state

    # 3. APPROVE LEAVE
    if "approve" in message:
        admin_emp = db.query(Employee).filter(Employee.email == user_id).first()
        admin_db_id = admin_emp.id if admin_emp else None
        
        name_target = extract_name(message, ["approve leave", "approve"])
        
        target_list = []
        if len(name_target) > 2:
            found_specific = False
            for leave in pending_leaves:
                emp = db.query(Employee).filter(Employee.id == leave.employee_id).first()
                if emp and name_target in emp.name.lower():
                    target_list.append(leave)
                    found_specific = True
            if not found_specific:
                state["messages"].append({"role": "assistant", "content": f"⚠️ No pending leave found for '{name_target}'."})
                return state
        else:
            target_list = pending_leaves

        if not target_list:
             state["messages"].append({"role": "assistant", "content": "✅ No requests to approve."})
             return state

        status_report = ""
        for leave in target_list:
            emp = db.query(Employee).filter(Employee.id == leave.employee_id).first()
            if not emp: continue
            
            target_email = emp.personal_email if emp.personal_email else emp.email
            approved = False
            reason = "Policy Violation"

            if leave.leave_type == "emergency":
                if emp.used_emergency_leaves <= 1.0: 
                    approved = True
                else: 
                    reason = "Emergency Quota Exceeded"
            elif leave.leave_type == "unpaid":
                approved = True
            else:
                reason = "Invalid Leave Type"

            if approved:
                leave.status = "approved"
                leave.approved_by = admin_db_id
                success = send_email(target_email, "Leave Request Approved", f"Dear {emp.name},\n\nYour {leave.leave_type} leave is APPROVED.")
                icon = "📧" if success else "⚠️"
                status_report += f"- ✅ Approved: {emp.name} ({leave.leave_type}) {icon}\n"
            else:
                leave.status = "rejected"
                days_cost = (leave.end_date - leave.start_date).days + 1
                if "half" in (leave.reason or "").lower(): days_cost = 0.5
                if leave.leave_type == "emergency": 
                    emp.used_emergency_leaves -= days_cost
                    if emp.used_emergency_leaves < 0: emp.used_emergency_leaves = 0

                success = send_email(target_email, "Leave Request Rejected", f"Dear {emp.name},\n\nREJECTED: {reason}.")
                icon = "📧" if success else "⚠️"
                status_report += f"- ❌ Rejected: {emp.name} ({reason}) {icon}\n"
        
        db.commit()
        state["notification"] = "✅ Requests Processed!"
        state["messages"].append({"role": "assistant", "content": f"**Processed:**\n{status_report}"})
        return state

    msg = "**Pending Leave Requests:**\n"
    for leave in pending_leaves:
        emp = db.query(Employee).filter(Employee.id == leave.employee_id).first()
        msg += f"- **{emp.name}**: {leave.leave_type.title()} ({leave.start_date.date()})\n"
    msg += "\nCommands:\n- **'Approve leaves [all]'**\n- **'Approve leave for [name]'**\n- **'Reject leave for [name]'**"
    state["messages"].append({"role": "assistant", "content": msg})

    return state