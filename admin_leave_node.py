# """
# admin_leave_node.py
# """
# """
# admin_leave_node.py
# """
# from models import LeaveRequest, Employee
# from email_service import send_email
# from datetime import datetime

# def admin_leave_node(state):
#     db = state["db"]
#     message = state.get("message", "").lower()
#     user_id = state["user_id"] # Admin's email
    
#     if "messages" not in state:
#         state["messages"] = []

#     # 1. Fetch Pending Requests
#     pending_leaves = db.query(LeaveRequest).filter(LeaveRequest.status == "pending_approval").all()

#     if not pending_leaves:
#         state["messages"].append({"role": "assistant", "content": "✅ No pending leave requests."})
#         return state

#     # 2. Approve Logic with BALANCE CHECK
#     if "approve" in message:
#         # Get Admin ID
#         admin_emp = db.query(Employee).filter(Employee.email == user_id).first()
#         admin_db_id = admin_emp.id if admin_emp else None

#         approved_count = 0
#         rejected_count = 0
        
#         status_report = ""

#         for leave in pending_leaves:
#             emp = db.query(Employee).filter(Employee.id == leave.employee_id).first()
#             if not emp: continue

#             # A. Calculate Days Requested (Inclusive)
#             # Example: 22nd to 22nd = 1 day
#             days_requested = (leave.end_date - leave.start_date).days + 1
            
#             # B. Check Balance
#             if emp.leaves_balance >= days_requested:
#                 # --- APPROVE ---
#                 emp.leaves_balance -= days_requested  # DEDUCT BALANCE
#                 leave.status = "approved"
#                 leave.approved_by = admin_db_id
                
#                 # Email Employee
#                 subject = "Leave Request Approved"
#                 body = (f"Dear {emp.name},\n\nYour leave for {days_requested} days has been APPROVED.\n"
#                         f"Remaining Balance: {emp.leaves_balance} days.\n\nBest,\nAdmin")
#                 try:
#                     send_email(to=emp.email, subject=subject, body=body)
#                 except:
#                     pass
                
#                 approved_count += 1
#                 status_report += f"- ✅ Approved: {emp.name} ({days_requested} days)\n"

#             else:
#                 # --- REJECT (Insufficient Balance) ---
#                 leave.status = "rejected"
                
#                 # Email Employee
#                 subject = "Leave Request Rejected"
#                 body = (f"Dear {emp.name},\n\nYour leave request for {days_requested} days was REJECTED.\n"
#                         f"Reason: Insufficient leave balance (Current: {emp.leaves_balance} days).\n\nBest,\nAdmin")
#                 try:
#                     send_email(to=emp.email, subject=subject, body=body)
#                 except:
#                     pass
                
#                 rejected_count += 1
#                 status_report += f"- ❌ Rejected: {emp.name} (Requested {days_requested}, Balance {emp.leaves_balance})\n"
        
#         db.commit()
        
#         final_msg = f"**Processed Requests:**\n{status_report}"
#         state["messages"].append({"role": "assistant", "content": final_msg})

#     # 3. List Logic (Show Balance Preview)
#     else:
#         msg = "**Pending Leave Requests:**\n| Employee | Type | Dates | Days | Current Balance |\n|---|---|---|---|---|\n"
#         for leave in pending_leaves:
#             emp = db.query(Employee).filter(Employee.id == leave.employee_id).first()
#             name = emp.name if emp else "Unknown"
#             balance = emp.leaves_balance if emp else 0
            
#             duration = (leave.end_date - leave.start_date).days + 1
            
#             msg += f"| {name} | {leave.type} | {leave.start_date.date()} to {leave.end_date.date()} | {duration} | {balance} |\n"
        
#         msg += "\nType **'approve leaves'** to process."
#         state["messages"].append({"role": "assistant", "content": msg})

#     return state


# """
# admin_leave_node.py
# """
# from models import LeaveRequest, Employee
# from email_service import send_email
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
from models import LeaveRequest, Employee
from email_service import send_email
from datetime import datetime

def extract_name(message, triggers):
    """Helper to extract name"""
    for t in triggers:
        message = message.replace(t, "")
    message = message.replace("for", "").strip()
    return message

def admin_leave_node(state):
    db = state["db"]
    message = state.get("message", "").lower()
    user_id = state["user_id"] 
    if "messages" not in state: state["messages"] = []

    # Get pending leaves safely
    pending_leaves = db.query(LeaveRequest).filter(LeaveRequest.status == "pending_approval").all()

    # ---------------------------------------------------------
    # 1. SHOW PENDING LEAVES
    # ---------------------------------------------------------
    if not pending_leaves and "approve" not in message and "reject" not in message:
        state["messages"].append({"role": "assistant", "content": "✅ No pending leave requests."})
        return state

    # ---------------------------------------------------------
    # 2. REJECT LEAVE (Manual)
    # ---------------------------------------------------------
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
            
            # Refund Balance if needed
            days_cost = (target_leave.end_date - target_leave.start_date).days + 1
            if "half" in (target_leave.reason or "").lower(): 
                 days_cost = 0.5

            # FIX: Use leave_type instead of type
            if target_leave.leave_type == "emergency":
                target_emp.used_emergency_leaves -= days_cost
                if target_emp.used_emergency_leaves < 0: target_emp.used_emergency_leaves = 0
            
            db.commit()
            send_email(target_emp.email, "Leave Request Rejected", f"Dear {target_emp.name},\n\nYour leave request has been REJECTED by Admin.")
            
            state["notification"] = f"🚫 Rejected leave for {target_emp.name}"
            state["messages"].append({"role": "assistant", "content": f"✅ **Rejected:** Leave for {target_emp.name} has been cancelled."})
        else:
            state["messages"].append({"role": "assistant", "content": f"⚠️ Could not find a pending request for '{name_target}'."})
        return state

    # ---------------------------------------------------------
    # 3. APPROVE LEAVE (Specific OR All)
    # ---------------------------------------------------------
    if "approve" in message:
        # Get Admin ID
        admin_emp = db.query(Employee).filter(Employee.email == user_id).first()
        admin_db_id = admin_emp.id if admin_emp else None
        
        name_target = extract_name(message, ["approve leave", "approve"])
        
        target_list = []
        
        # If user typed a specific name (e.g. "Approve leave for Ram")
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
            # "Approve leaves" -> Approve ALL
            target_list = pending_leaves

        if not target_list:
             state["messages"].append({"role": "assistant", "content": "✅ No requests to approve."})
             return state

        # Process the selected list
        status_report = ""
        for leave in target_list:
            emp = db.query(Employee).filter(Employee.id == leave.employee_id).first()
            if not emp: continue
            
            target_email = emp.personal_email if emp.personal_email else emp.email
            approved = False
            reason = "Policy Violation"

            # FIX: Use leave_type instead of type
            if leave.leave_type == "emergency":
                # Check if they have used less than limit (Assuming limit is 1.0)
                # If used_emergency_leaves is 0, they can take 1.
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
                send_email(target_email, "Leave Request Approved", f"Dear {emp.name},\n\nYour {leave.leave_type} leave is APPROVED.")
                status_report += f"- ✅ Approved: {emp.name} ({leave.leave_type})\n"
            else:
                leave.status = "rejected"
                # Refund logic
                days_cost = (leave.end_date - leave.start_date).days + 1
                if "half" in (leave.reason or "").lower(): days_cost = 0.5
                
                # FIX: Use leave_type
                if leave.leave_type == "emergency": 
                    emp.used_emergency_leaves -= days_cost
                    if emp.used_emergency_leaves < 0: emp.used_emergency_leaves = 0

                send_email(target_email, "Leave Request Rejected", f"Dear {emp.name},\n\nREJECTED: {reason}.")
                status_report += f"- ❌ Rejected: {emp.name} ({reason})\n"
        
        db.commit()
        state["notification"] = "✅ Requests Processed!"
        state["messages"].append({"role": "assistant", "content": f"**Processed:**\n{status_report}"})
        return state

    # ---------------------------------------------------------
    # 4. DASHBOARD (Default View)
    # ---------------------------------------------------------
    msg = "**Pending Leave Requests:**\n"
    for leave in pending_leaves:
        emp = db.query(Employee).filter(Employee.id == leave.employee_id).first()
        # FIX: Use leave_type
        msg += f"- **{emp.name}**: {leave.leave_type.title()} ({leave.start_date.date()})\n"
    
    msg += "\nCommands:\n- **'Approve leaves'** (Process ALL)\n- **'Approve leave for [name]'**\n- **'Reject leave for [name]'**"
    state["messages"].append({"role": "assistant", "content": msg})

    return state