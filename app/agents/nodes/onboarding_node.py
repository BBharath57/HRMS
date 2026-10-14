
# """
# onboarding_node.py
# """
# from app.database.models import Employee, Onboarding
# from app.services.email_service import send_email

# def onboarding_node(state):
#     db = state["db"]
#     user_id = state["user_id"]
#     user_input = state.get("message", "").strip()

#     # --- RESET COMMAND ---
#     if "reset" in user_input.lower():
#         employee = db.query(Employee).filter(Employee.email == user_id).first()
#         if employee:
#             db.query(Onboarding).filter(Onboarding.employee_id == employee.id).delete()
#             employee.onboarding_status = "pending"
#             # Reset fields
#             employee.leaves_balance = 24
#             db.commit()
#             state["messages"].append({"role": "assistant", "content": "🔄 Onboarding reset. Type 'start onboarding'."})
#             state["onboarding_active"] = False
#             return state

#     # --- INITIALIZATION ---
#     state["onboarding_active"] = True
#     employee = db.query(Employee).filter(Employee.email == user_id).first()
    
#     if not employee:
#         state["messages"].append({"role": "assistant", "content": "❌ User not found."})
#         state["onboarding_active"] = False
#         return state

#     onboarding = db.query(Onboarding).filter(Onboarding.employee_id == employee.id).first()

#     if not onboarding:
#         onboarding = Onboarding(employee_id=employee.id, step=1, data="", completed=False)
#         db.add(onboarding)
#         db.commit()
#         state["messages"].append({"role": "assistant", "content": "👋 Welcome! Let's get your details.\n\n**Step 1:** What is your **Full Name**?"})
#         return state

#     if onboarding.completed:
#         status_msg = "✅ Onboarding Completed." if employee.onboarding_status == "completed" else "⏳ Waiting for Admin Approval."
#         state["messages"].append({"role": "assistant", "content": status_msg})
#         state["onboarding_active"] = False
#         return state

#     # --- STEPS LOGIC ---
#     response_text = ""
#     is_start = any(x in user_input.lower() for x in ["start", "begin"])

#     # Step 1: Name
#     if onboarding.step == 1:
#         if not is_start:
#             employee.name = user_input
#             onboarding.data += f"Name: {user_input}\n"
#             onboarding.step = 2
#             response_text = "Got it. **Step 2:** What is your **Current Address**?"
#         else:
#             response_text = "Step 1: What is your **Full Name**?"

#     # Step 2: Address
#     elif onboarding.step == 2:
#         onboarding.data += f"Address: {user_input}\n"
#         onboarding.step = 3
#         response_text = "**Step 3:** What is your **Contact Number**?"

#     # Step 3: Contact
#     elif onboarding.step == 3:
#         onboarding.data += f"Contact: {user_input}\n"
#         onboarding.step = 4
#         response_text = "**Step 4:** What is your **Personal Email**?"

#     # Step 4: Personal Email
#     elif onboarding.step == 4:
#         employee.personal_email = user_input
#         onboarding.data += f"Personal Email: {user_input}\n"
#         onboarding.step = 5
#         response_text = "**Step 5:** What is your **Date of Birth**? (YYYY-MM-DD)"

#     # Step 5: DOB
#     elif onboarding.step == 5:
#         employee.dob = user_input
#         onboarding.data += f"DOB: {user_input}\n"
#         onboarding.step = 6
#         response_text = "**Step 6:** What is your **Age**?"

#     # Step 6: Age
#     elif onboarding.step == 6:
#         if user_input.isdigit():
#             employee.age = int(user_input)
#             onboarding.data += f"Age: {user_input}\n"
#             onboarding.step = 7
#             response_text = "**Step 7:** What is your **Nationality**?"
#         else:
#             response_text = "⚠️ Please enter a valid number for Age."

#     # Step 7: Nationality
#     elif onboarding.step == 7:
#         employee.nationality = user_input
#         onboarding.data += f"Nationality: {user_input}\n"
#         onboarding.step = 8
#         response_text = "**Step 8:** Are you a **Developer** or **Non-Tech**? (Enter Role)"

#     # Step 8: Role
#     elif onboarding.step == 8:
#         employee.role = user_input
#         # Allocate Leaves (Default 24)
#         employee.leaves_balance = 24 
#         onboarding.data += f"Role: {user_input}\nAllocated Leaves: 24\n"
#         onboarding.step = 9
        
#         # --- SHOW AGREEMENT ---
#         agreement_text = (
#             "📜 **Terms of Employment & Background Check Agreement**\n\n"
#             "I certify that all statements made in this application are true. "
#             "I authorize **Your Volta Services Pvt Ltd** to conduct background checks regarding my education, employment history, and criminal record. "
#             "I understand that any misrepresentation may result in dismissal. "
#             "I agree to the company's data sharing policies for client requirements.\n\n"
#             "**Do you agree with these terms and conditions? (Type 'Yes' or 'No')**"
#         )
#         response_text = agreement_text

#     # Step 9: Agreement Confirmation
#     elif onboarding.step == 9:
#         if "yes" in user_input.lower():
#             onboarding.data += "Agreement Accepted: YES\n"
#             onboarding.completed = True
#             employee.onboarding_status = "pending_approval"
            
#             # Email Admin
#             admin_body = (
#                 f"New Onboarding Request:\n"
#                 f"Name: {employee.name}\n"
#                 f"Role: {employee.role}\n"
#                 f"Email: {employee.personal_email}\n"
#                 f"DOB: {employee.dob} (Age: {employee.age})\n"
#                 f"Nationality: {employee.nationality}\n"
#                 f"Full Data:\n{onboarding.data}"
#             )
#             send_email("bharathkumarking143@gmail.com", "Action Required: Approve Onboarding", admin_body)
            
#             response_text = "✅ **Agreement Signed.** Your details have been submitted to Admin for approval."
#             state["onboarding_active"] = False
#         else:
#             response_text = "❌ You must agree to the terms to proceed. Type **'Yes'** to accept or **'Reset'** to cancel."

#     db.commit()
#     if response_text:
#         state["messages"].append({"role": "assistant", "content": response_text})

#     return state


"""
onboarding_node.py
"""
# from app.database.models import Employee, Onboarding
# from app.services.email_service import send_email

# def onboarding_node(state):
#     db = state["db"]
#     user_id = state["user_id"]
#     user_input = state.get("message", "").strip()

#     if "reset" in user_input.lower():
#         employee = db.query(Employee).filter(Employee.email == user_id).first()
#         if employee:
#             db.query(Onboarding).filter(Onboarding.employee_id == employee.id).delete()
#             employee.onboarding_status = "pending"
#             employee.leaves_balance = 24
#             db.commit()
#             state["messages"].append({"role": "assistant", "content": "🔄 Onboarding reset. Type 'start onboarding'."})
#             state["onboarding_active"] = False
#             return state

#     state["onboarding_active"] = True
#     employee = db.query(Employee).filter(Employee.email == user_id).first()
#     if not employee: return state # safety check

#     onboarding = db.query(Onboarding).filter(Onboarding.employee_id == employee.id).first()
#     if not onboarding:
#         onboarding = Onboarding(employee_id=employee.id, step=1, data="", completed=False)
#         db.add(onboarding); db.commit()
#         state["messages"].append({"role": "assistant", "content": "👋 Welcome! Let's get your details.\n\n**Step 1:** What is your **Full Name**?"})
#         return state

#     if onboarding.completed:
#         status_msg = "✅ Onboarding Completed." if employee.onboarding_status == "completed" else "⏳ Waiting for Admin Approval."
#         state["messages"].append({"role": "assistant", "content": status_msg})
#         state["onboarding_active"] = False
#         return state

#     response_text = ""
#     is_start = any(x in user_input.lower() for x in ["start", "begin"])

#     # Steps 1-8 (Same as before)
#     if onboarding.step == 1:
#         if not is_start: employee.name = user_input; onboarding.data += f"Name: {user_input}\n"; onboarding.step = 2; response_text = "Got it. **Step 2:** What is your **Current Address**?"
#         else: response_text = "Step 1: What is your **Full Name**?"
#     elif onboarding.step == 2: onboarding.data += f"Address: {user_input}\n"; onboarding.step = 3; response_text = "**Step 3:** What is your **Contact Number**?"
#     elif onboarding.step == 3: onboarding.data += f"Contact: {user_input}\n"; onboarding.step = 4; response_text = "**Step 4:** What is your **Personal Email**?"
#     elif onboarding.step == 4: employee.personal_email = user_input; onboarding.data += f"Personal Email: {user_input}\n"; onboarding.step = 5; response_text = "**Step 5:** What is your **Date of Birth**? (YYYY-MM-DD)"
#     elif onboarding.step == 5: employee.dob = user_input; onboarding.data += f"DOB: {user_input}\n"; onboarding.step = 6; response_text = "**Step 6:** What is your **Age**?"
#     elif onboarding.step == 6:
#         if user_input.isdigit(): employee.age = int(user_input); onboarding.data += f"Age: {user_input}\n"; onboarding.step = 7; response_text = "**Step 7:** What is your **Nationality**?"
#         else: response_text = "⚠️ Please enter a valid number."
#     elif onboarding.step == 7: employee.nationality = user_input; onboarding.data += f"Nationality: {user_input}\n"; onboarding.step = 8; response_text = "**Step 8:** Are you a **Developer** or **Non-Tech**?"
#     elif onboarding.step == 8:
#         employee.role = user_input; employee.leaves_balance = 24
#         onboarding.data += f"Role: {user_input}\nAllocated Leaves: 24\n"; onboarding.step = 9
#         response_text = "📜 **Terms & Conditions**\nI authorize background checks...\n\n**Do you agree? (Type 'Yes')**"

#     # Step 9: Agreement
#     elif onboarding.step == 9:
#         if "yes" in user_input.lower():
#             onboarding.data += "Agreement Accepted: YES\n"; onboarding.completed = True; employee.onboarding_status = "pending_approval"
#             admin_body = f"New Onboarding:\nName: {employee.name}\nRole: {employee.role}\nFull Data:\n{onboarding.data}"
#             send_email("bharathkumarking143@gmail.com", "Action Required: Approve Onboarding", admin_body)
            
#             # --- NOTIFICATION ---
#             state["notification"] = "🚀 Onboarding Submitted Successfully!"
#             # --------------------

#             response_text = "✅ **Agreement Signed.** Details submitted to Admin."
#             state["onboarding_active"] = False
#         else:
#             response_text = "❌ Type **'Yes'** to accept."

#     db.commit()
#     if response_text: state["messages"].append({"role": "assistant", "content": response_text})
#     return state


"""
onboarding_node.py
"""
from app.database.models import Employee, Onboarding
from app.services.email_service import send_email

def onboarding_node(state):
    db = state["db"]
    user_id = state["user_id"]
    user_input = state.get("message", "").strip()
    
    employee = db.query(Employee).filter(Employee.email == user_id).first()
    
    # Trigger logic
    if not state.get("onboarding_active"):
        # Only start if explicitly asked OR if status is 'onboarding_triggered' and user says 'yes'
        if "yes" in user_input.lower() and employee.onboarding_status == "onboarding_triggered":
            state["onboarding_active"] = True
        elif "start" in user_input.lower():
             state["onboarding_active"] = True
        else:
             return state # Should not happen due to routing

    # Setup Onboarding Entry
    onboarding = db.query(Onboarding).filter(Onboarding.employee_id == employee.id).first()
    if not onboarding:
        onboarding = Onboarding(employee_id=employee.id, step=1, data="")
        db.add(onboarding); db.commit()
        state["messages"].append({"role": "assistant", "content": "Great! **Step 1:** What is your **Full Name**?"})
        return state

    response_text = ""
    
    # STEPS (Simplified for brevity, same as before but updates DB fields)
    if onboarding.step == 1:
        employee.name = user_input; onboarding.data += f"Name: {user_input}\n"; onboarding.step = 2; response_text = "**Step 2:** What is your **Address**?"
    elif onboarding.step == 2:
        employee.address = user_input; onboarding.data += f"Address: {user_input}\n"; onboarding.step = 3; response_text = "**Step 3:** What is your **Date of Birth**?"
    elif onboarding.step == 3:
        employee.dob = user_input; onboarding.data += f"DOB: {user_input}\n"; onboarding.step = 4; response_text = "**Step 4:** What is your **Nationality**?"
    elif onboarding.step == 4:
        employee.nationality = user_input; onboarding.data += f"Nationality: {user_input}\n"; onboarding.step = 5; response_text = "**Step 5:** Type **'Submit'** to finish."
    
    # COMPLETION
    elif onboarding.step == 5:
        onboarding.completed = True
        # Manager Point 2.4: Update Status to 'details_submitted'
        employee.onboarding_status = "details_submitted"
        db.commit()
        
        # Email Admin
        admin_email = os.getenv("SENDER_EMAIL") # Or fetch from DB
        send_email(admin_email, "Action: Onboarding Details Filled", f"User {employee.name} has filled their details.\nPlease login to Admin Chat to finalize onboarding.\nlink: https://hrmsagent.streamlit.app/")
        
        response_text = "✅ **Details Submitted!** I have notified the Admin. Please wait for your Offer Letter."
        state["onboarding_active"] = False

    db.commit()
    if response_text: state["messages"].append({"role": "assistant", "content": response_text})
    return state