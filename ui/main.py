# import streamlit as st
# import os
# import sys

# # --- PATH FIX ---
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
# sys.path.insert(0, parent_dir)

# from db import get_db
# from models import Employee, Onboarding, LeaveRequest
# from rag_pipeline import retriever, llm
# from hr_graph import build_graph

# # --- PAGE CONFIG ---
# st.set_page_config(page_title="Agentic HR Assistant", layout="centered")
# st.title("🤖 Agentic HR Assistant")

# # --- CSS ---
# st.markdown("""
# <style>
#     .stChatMessage.st-emotion-cache-16idsys.eeusbqq4 { flex-direction: row-reverse; text-align: right; }
#     table { width: 100%; border-collapse: collapse; }
#     th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
#     th { background-color: #f2f2f2; }
# </style>
# """, unsafe_allow_html=True)

# # --- 1. SETUP ---
# db = next(get_db())
# REAL_EMPLOYEE_EMAIL = "bharathkumarking143@gmail.com" 
# REAL_ADMIN_EMAIL = "bharathkumarking143@gmail.com"

# # --- 2. MULTI-SESSION MEMORY ---
# if "role_sessions" not in st.session_state:
#     st.session_state.role_sessions = {
#         "employee": {"messages": [], "graph_context": {"onboarding_active": False, "leave_draft": {}}},
#         "admin": {"messages": [], "graph_context": {"onboarding_active": False, "leave_draft": {}}}
#     }

# # --- 3. SIDEBAR & NOTIFICATIONS (NEW) ---
# role = st.sidebar.radio("Role", ["employee", "admin"])
# user_email = REAL_EMPLOYEE_EMAIL if role == "employee" else REAL_ADMIN_EMAIL

# # Check DB for User
# user = db.query(Employee).filter(Employee.email == user_email).first()
# if not user:
#     user = Employee(name="New User", email=user_email, role=role)
#     db.add(user); db.commit()

# # --- NOTIFICATION BADGE (THE FIX) ---
# if role == "admin":
#     p_onboard = db.query(Onboarding).join(Employee).filter(Employee.onboarding_status == "pending_approval").count()
#     p_leave = db.query(LeaveRequest).filter(LeaveRequest.status == "pending_approval").count()
#     total_pending = p_onboard + p_leave
    
#     if total_pending > 0:
#         st.sidebar.error(f"🔔 **{total_pending} Actions Required**")
#         st.sidebar.caption(f"• {p_onboard} Onboarding\n• {p_leave} Leaves")
#     else:
#         st.sidebar.success("✅ All Caught Up")

# # --- 4. LOAD SESSION ---
# current_session = st.session_state.role_sessions[role]
# current_messages = current_session["messages"]
# current_context = current_session["graph_context"]
# graph = build_graph(db, retriever, llm)

# # --- 5. RENDER HISTORY ---
# for msg in current_messages:
#     avatar = "🤖" if msg["role"] == "assistant" else "🧑‍💻"
#     with st.chat_message(msg["role"], avatar=avatar):
#         st.markdown(msg["content"])

# # --- 6. INPUT ---
# user_input = st.chat_input(f"Message as {role.title()}...")

# if user_input:
#     with st.chat_message("user", avatar="🧑‍💻"): st.markdown(user_input)
#     current_messages.append({"role": "user", "content": user_input})

#     initial_state = {
#         "message": user_input, "user_id": user_email, "role": role, "messages": current_messages, 
#         "db": db, "retriever": retriever, "llm": llm, "db_user": user,
#         "onboarding_active": current_context["onboarding_active"], "leave_draft": current_context["leave_draft"],
#     }

#     try:
#         triggers = ["start onboarding", "join company", "write email", "apply leave", "request leave", "reset onboarding"]
#         is_active = any(t in user_input.lower() for t in triggers) or initial_state["onboarding_active"] or initial_state["leave_draft"]

#         if is_active:
#             with st.status("🤖 Agent Working...", expanded=True) as status:
#                 final_state = graph.invoke(initial_state)
#                 status.update(label="✅ Processed", state="complete", expanded=False)
#         else:
#             with st.spinner("🤖 Thinking..."):
#                 final_state = graph.invoke(initial_state)

#         current_session["messages"] = final_state["messages"] 
#         current_session["graph_context"]["onboarding_active"] = final_state.get("onboarding_active", False)
#         current_session["graph_context"]["leave_draft"] = final_state.get("leave_draft", {})

#         last_message = final_state["messages"][-1]
#         if last_message["role"] == "assistant":
#             with st.chat_message("assistant", avatar="🤖"):
#                 st.markdown(last_message["content"])

#     except Exception as e:
#         st.error(f"System Error: {e}")
        

# this the one
# import streamlit as st
# import os
# import sys
# from sqlalchemy import desc  # <--- Added for sorting

# # --- PATH FIX ---
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
# sys.path.insert(0, parent_dir)

# from db import get_db
# from models import Employee, Onboarding, LeaveRequest
# from rag_pipeline import retriever, llm
# from hr_graph import build_graph

# # --- PAGE CONFIG ---
# st.set_page_config(page_title="Office Assistant", layout="centered")

# # --- CSS ---
# st.markdown("""
# <style>
#     .stChatMessage.st-emotion-cache-16idsys.eeusbqq4 { flex-direction: row-reverse; text-align: right; }
#     table { width: 100%; border-collapse: collapse; }
#     th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
#     th { background-color: #f2f2f2; }
#     .stButton button { width: 100%; height: 80px; font-size: 20px; font-weight: bold; }
# </style>
# """, unsafe_allow_html=True)

# # --- 1. SESSION STATE INITIALIZATION ---
# if "role" not in st.session_state:
#     st.session_state.role = None

# # Track Previous States for "Push" Notifications
# if "tracker" not in st.session_state:
#     st.session_state.tracker = {
#         "admin_pending_count": 0,
#         "emp_leave_status": None,
#         "emp_onboard_status": None
#     }

# if "role_sessions" not in st.session_state:
#     st.session_state.role_sessions = {
#         "employee": {"messages": [], "graph_context": {"onboarding_active": False, "leave_draft": {}}},
#         "admin": {"messages": [], "graph_context": {"onboarding_active": False, "leave_draft": {}}}
#     }

# # --- 2. DB SETUP ---
# db = next(get_db())
# REAL_EMPLOYEE_EMAIL = "bharathkumarking143@gmail.com" 
# REAL_ADMIN_EMAIL = "bharathkumarking143@gmail.com"

# # ==========================================
# #      LANDING PAGE (LOGIN)
# # ==========================================
# if st.session_state.role is None:
#     st.title("🏢 Office Assistant")
#     st.write("### Please select your role to continue:")
#     st.write("") 
#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("🔒 Admin"):
#             st.session_state.role = "admin"
#             st.rerun()
#     with col2:
#         if st.button("🧑‍💻 Employee"):
#             st.session_state.role = "employee"
#             st.rerun()
#     st.info("Select a role above to enter the chat workspace.")

# # ==========================================
# #      CHAT INTERFACE
# # ==========================================
# else:
#     role = st.session_state.role
#     user_email = REAL_EMPLOYEE_EMAIL if role == "employee" else REAL_ADMIN_EMAIL

#     # --- ENSURE USER EXISTS ---
#     user = db.query(Employee).filter(Employee.email == user_email).first()
#     if not user:
#         user = Employee(name="New User", email=user_email, role=role)
#         db.add(user); db.commit()

#     # ==========================================
#     # 🔔 REAL-TIME NOTIFICATION SYSTEM (POLLING)
#     # ==========================================
#     # This block checks the DB every time the script runs (interaction/refresh)
    
#     if role == "admin":
#         # 1. Count Pending Items
#         p_onboard = db.query(Onboarding).join(Employee).filter(Employee.onboarding_status == "pending_approval").count()
#         p_leave = db.query(LeaveRequest).filter(LeaveRequest.status == "pending_approval").count()
#         current_total = p_onboard + p_leave
        
#         # 2. Compare with Last Known Count
#         last_count = st.session_state.tracker["admin_pending_count"]
        
#         # If count INCREASED, it means a new request came in!
#         if current_total > last_count:
#             st.toast(f"🔔 You have {current_total} Pending Requests!", icon="📩")
        
#         # Update Tracker
#         st.session_state.tracker["admin_pending_count"] = current_total

#     elif role == "employee":
#         # 1. Check Leave Status
#         last_leave = db.query(LeaveRequest).filter(LeaveRequest.employee_id == user.id).order_by(desc(LeaveRequest.created_at)).first()
#         if last_leave:
#             curr_status = last_leave.status
#             prev_status = st.session_state.tracker["emp_leave_status"]
            
#             # If status CHANGED from Pending -> Approved/Rejected
#             if prev_status and curr_status != prev_status:
#                 if curr_status == "approved":
#                     st.toast("🎉 Your Leave Request was APPROVED!", icon="✅")
#                 elif curr_status == "rejected":
#                     st.toast("⚠️ Your Leave Request was REJECTED.", icon="❌")
            
#             st.session_state.tracker["emp_leave_status"] = curr_status

#         # 2. Check Onboarding Status
#         curr_onboard = user.onboarding_status
#         prev_onboard = st.session_state.tracker["emp_onboard_status"]
        
#         if prev_onboard and curr_onboard != prev_onboard and curr_onboard == "completed":
#              st.toast("🎉 Onboarding Approved! You are set.", icon="✅")
        
#         st.session_state.tracker["emp_onboard_status"] = curr_onboard
#     # ==========================================

#     # --- SIDEBAR ---
#     with st.sidebar:
#         st.write(f"Logged in as: **{role.title()}**")
#         if st.button("⬅️ Switch Role / Logout"):
#             st.session_state.role = None
#             st.rerun()
#         st.divider()
        
#         # Sidebar Badges
#         if role == "admin":
#             if st.session_state.tracker["admin_pending_count"] > 0:
#                 st.error(f"🔔 **{st.session_state.tracker['admin_pending_count']} Actions**")
#             else:
#                 st.success("✅ All Caught Up")

#     # --- CHAT UI ---
#     st.title(f"💬 {role.title()} Chat")

#     current_session = st.session_state.role_sessions[role]
#     current_messages = current_session["messages"]
#     current_context = current_session["graph_context"]
#     graph = build_graph(db, retriever, llm)

#     for msg in current_messages:
#         avatar = "🤖" if msg["role"] == "assistant" else "🧑‍💻"
#         with st.chat_message(msg["role"], avatar=avatar):
#             st.markdown(msg["content"])

#     user_input = st.chat_input(f"Message as {role.title()}...")

#     if user_input:
#         with st.chat_message("user", avatar="🧑‍💻"): st.markdown(user_input)
#         current_messages.append({"role": "user", "content": user_input})

#         initial_state = {
#             "message": user_input, "user_id": user_email, "role": role, "messages": current_messages, 
#             "db": db, "retriever": retriever, "llm": llm, "db_user": user,
#             "onboarding_active": current_context["onboarding_active"], "leave_draft": current_context["leave_draft"],
#             "notification": None
#         }

#         try:
#             triggers = ["start onboarding", "join company", "write email", "apply leave", "request leave", "reset onboarding"]
#             is_active = any(t in user_input.lower() for t in triggers) or initial_state["onboarding_active"] or initial_state["leave_draft"]

#             if is_active:
#                 with st.status("🤖 Agent Working...", expanded=True) as status:
#                     final_state = graph.invoke(initial_state)
#                     status.update(label="✅ Processed", state="complete", expanded=False)
#             else:
#                 with st.spinner("🤖 Thinking..."):
#                     final_state = graph.invoke(initial_state)

#             # --- ACTION TOAST (Self-Triggered) ---
#             if final_state.get("notification"):
#                 st.toast(final_state["notification"], icon="🚀")

#             current_session["messages"] = final_state["messages"] 
#             current_session["graph_context"]["onboarding_active"] = final_state.get("onboarding_active", False)
#             current_session["graph_context"]["leave_draft"] = final_state.get("leave_draft", {})

#             last_message = final_state["messages"][-1]
#             if last_message["role"] == "assistant":
#                 with st.chat_message("assistant", avatar="🤖"):
#                     st.markdown(last_message["content"])

#         except Exception as e:
#             st.error(f"System Error: {e}")



# import streamlit as st
# import os
# import sys

# # --- PATH FIX ---
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
# sys.path.insert(0, parent_dir)

# from db import get_db
# from models import Employee, Onboarding, LeaveRequest
# from rag_pipeline import retriever, llm
# from hr_graph import build_graph

# # --- PAGE CONFIG ---
# st.set_page_config(page_title="Agentic HR Assistant", layout="centered")

# # --- CSS STYLING ---
# st.markdown("""
# <style>
#     /* Title styling */
#     .main-title {
#         text-align: center;
#         color: #1E3A8A;
#         margin-bottom: 2rem;
#         padding: 1rem;
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         border-radius: 15px;
#         box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#     }
    
#     /* Role selection cards */
#     .role-card {
#         border: 2px solid #E5E7EB;
#         border-radius: 12px;
#         padding: 2rem;
#         text-align: center;
#         cursor: pointer;
#         transition: all 0.3s ease;
#         background: white;
#         margin: 1rem 0;
#     }
    
#     .role-card:hover {
#         transform: translateY(-5px);
#         border-color: #3B82F6;
#         box-shadow: 0 10px 25px rgba(59, 130, 246, 0.1);
#     }
    
#     .role-card.selected {
#         border-color: #3B82F6;
#         background: linear-gradient(135deg, #EBF4FF 0%, #E0F2FE 100%);
#     }
    
#     .role-icon {
#         font-size: 3rem;
#         margin-bottom: 1rem;
#     }
    
#     .role-title {
#         font-size: 1.5rem;
#         font-weight: 600;
#         color: #1F2937;
#         margin-bottom: 0.5rem;
#     }
    
#     .role-desc {
#         color: #6B7280;
#         font-size: 0.9rem;
#     }
    
#     /* Chat message styling */
#     .stChatMessage.st-emotion-cache-16idsys.eeusbqq4 { 
#         flex-direction: row-reverse; 
#         text-align: right; 
#     }
    
#     /* Status badges */
#     .status-badge {
#         display: inline-block;
#         padding: 0.25rem 0.75rem;
#         border-radius: 20px;
#         font-size: 0.75rem;
#         font-weight: 600;
#         margin-left: 0.5rem;
#     }
    
#     .badge-pending {
#         background-color: #FEF3C7;
#         color: #92400E;
#     }
    
#     .badge-approved {
#         background-color: #D1FAE5;
#         color: #065F46;
#     }
# </style>
# """, unsafe_allow_html=True)

# # --- 1. SETUP ---
# db = next(get_db())
# REAL_EMPLOYEE_EMAIL = "bharathkumarking143@gmail.com" 
# REAL_ADMIN_EMAIL = "bharathkumarking143@gmail.com"

# # --- 2. MULTI-SESSION MEMORY ---
# if "role_sessions" not in st.session_state:
#     st.session_state.role_sessions = {
#         "employee": {"messages": [], "graph_context": {"onboarding_active": False, "leave_draft": {}}},
#         "admin": {"messages": [], "graph_context": {"onboarding_active": False, "leave_draft": {}}}
#     }

# # --- 3. ROLE SELECTION PAGE ---
# st.markdown('<div class="main-title"><h1>🏢 Office Assistant</h1></div>', unsafe_allow_html=True)

# # Initialize selected role in session state
# if 'selected_role' not in st.session_state:
#     st.session_state.selected_role = None

# # If no role selected, show selection page
# if st.session_state.selected_role is None:
#     st.markdown("### 👥 Select Your Role")
#     st.markdown("Choose your role to access the appropriate chat interface:")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.markdown("""
#         <div class="role-card" id="admin-card">
#             <div class="role-icon">👑</div>
#             <div class="role-title">Administrator</div>
#             <div class="role-desc">Manage employees, approve requests, and view all system data</div>
#         </div>
#         """, unsafe_allow_html=True)
#         admin_clicked = st.button("Enter as Admin", key="admin_btn", type="primary", use_container_width=True)
        
#     with col2:
#         st.markdown("""
#         <div class="role-card" id="employee-card">
#             <div class="role-icon">👤</div>
#             <div class="role-title">Employee</div>
#             <div class="role-desc">Check your details, apply for leaves, and get HR assistance</div>
#         </div>
#         """, unsafe_allow_html=True)
#         employee_clicked = st.button("Enter as Employee", key="employee_btn", use_container_width=True)
    
#     # Handle role selection
#     if admin_clicked:
#         st.session_state.selected_role = "admin"
#         st.rerun()
#     elif employee_clicked:
#         st.session_state.selected_role = "employee"
#         st.rerun()
    
#     st.markdown("---")
#     st.caption("⚠️ Once you select a role, you cannot switch to the other role in this session.")
#     st.stop()

# # --- 4. CHAT INTERFACE (AFTER ROLE SELECTION) ---
# role = st.session_state.selected_role
# user_email = REAL_EMPLOYEE_EMAIL if role == "employee" else REAL_ADMIN_EMAIL

# # Check DB for User
# user = db.query(Employee).filter(Employee.email == user_email).first()
# if not user:
#     user = Employee(name="New User", email=user_email, role=role)
#     db.add(user)
#     db.commit()

# # Display role header with styling
# header_col1, header_col2 = st.columns([3, 1])
# with header_col1:
#     if role == "admin":
#         st.markdown(f"## 👑 Administrator Chat")
#         # Show pending requests for admin
#         p_onboard = db.query(Onboarding).join(Employee).filter(Employee.onboarding_status == "pending_approval").count()
#         p_leave = db.query(LeaveRequest).filter(LeaveRequest.status == "pending_approval").count()
#         total_pending = p_onboard + p_leave
        
#         if total_pending > 0:
#             st.markdown(f"""
#             <div style="background-color: #FEF3C7; padding: 0.5rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
#                 🔔 **{total_pending} Action(s) Required**  
#                 • {p_onboard} Onboarding request(s)  
#                 • {p_leave} Leave request(s)
#             </div>
#             """, unsafe_allow_html=True)
#     else:
#         st.markdown(f"## 👤 Employee Chat")
        
#         # Show leave balance for employee
#         remaining_leaves = user.leaves_balance
#         allocated_leaves = 24
#         used_leaves = allocated_leaves - remaining_leaves
        
#         st.markdown(f"""
#         <div style="background-color: #E0F2FE; padding: 0.5rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
#             📊 **Your Leave Status:**  
#             • Allocated: {allocated_leaves} days  
#             • Used: {used_leaves} days  
#             • Remaining: {remaining_leaves} days
#         </div>
#         """, unsafe_allow_html=True)

# with header_col2:
#     # Logout/Reset button
#     if st.button("🔄 Restart", type="secondary"):
#         st.session_state.selected_role = None
#         st.session_state.role_sessions[role]["messages"] = []
#         st.session_state.role_sessions[role]["graph_context"] = {"onboarding_active": False, "leave_draft": {}}
#         st.rerun()

# st.markdown("---")

# # --- 5. LOAD SESSION FOR SELECTED ROLE ---
# current_session = st.session_state.role_sessions[role]
# current_messages = current_session["messages"]
# current_context = current_session["graph_context"]
# graph = build_graph(db, retriever, llm)

# # --- 6. RENDER CHAT HISTORY ---
# for msg in current_messages:
#     if msg["role"] == "assistant":
#         with st.chat_message("assistant", avatar="🤖"):
#             st.markdown(msg["content"])
#     else:
#         with st.chat_message("user", avatar="👑" if role == "admin" else "👤"):
#             st.markdown(msg["content"])

# # --- 7. CHAT INPUT ---
# user_input = st.chat_input(f"Type your message as {role.title()}...")

# if user_input:
#     # Display user message
#     with st.chat_message("user", avatar="👑" if role == "admin" else "👤"):
#         st.markdown(user_input)
    
#     # Add to messages
#     current_messages.append({"role": "user", "content": user_input})

#     # Prepare state for graph
#     initial_state = {
#         "message": user_input, 
#         "user_id": user_email, 
#         "role": role, 
#         "messages": current_messages, 
#         "db": db, 
#         "retriever": retriever, 
#         "llm": llm, 
#         "db_user": user,
#         "onboarding_active": current_context["onboarding_active"], 
#         "leave_draft": current_context["leave_draft"],
#     }

#     try:
#         # Determine if we need expanded status
#         triggers = ["start onboarding", "join company", "write email", "apply leave", "request leave", "reset onboarding"]
#         is_active = any(t in user_input.lower() for t in triggers) or initial_state["onboarding_active"] or initial_state["leave_draft"]

#         if is_active:
#             with st.status("🤖 Processing your request...", expanded=True) as status:
#                 final_state = graph.invoke(initial_state)
#                 status.update(label="✅ Request processed", state="complete", expanded=False)
#         else:
#             with st.spinner("🤖 Thinking..."):
#                 final_state = graph.invoke(initial_state)

#         # Update session state
#         current_session["messages"] = final_state["messages"] 
#         current_session["graph_context"]["onboarding_active"] = final_state.get("onboarding_active", False)
#         current_session["graph_context"]["leave_draft"] = final_state.get("leave_draft", {})

#         # Display assistant response
#         last_message = final_state["messages"][-1]
#         if last_message["role"] == "assistant":
#             with st.chat_message("assistant", avatar="🤖"):
#                 st.markdown(last_message["content"])

#     except Exception as e:
#         st.error(f"❌ System Error: {e}")
#         st.info("Try refreshing the page or restarting the chat.")

# # --- 8. QUICK ACTIONS (Optional) ---
# st.markdown("---")
# st.markdown("### 💡 Quick Actions")

# if role == "admin":
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         if st.button("📋 Show All Employees", use_container_width=True):
#             st.session_state.role_sessions[role]["messages"].append({"role": "user", "content": "show all the employee details"})
#             st.rerun()
#     with col2:
#         if st.button("🔔 Check Pending", use_container_width=True):
#             st.session_state.role_sessions[role]["messages"].append({"role": "user", "content": "any pending requests"})
#             st.rerun()
#     with col3:
#         if st.button("📊 Leave Dashboard", use_container_width=True):
#             st.session_state.role_sessions[role]["messages"].append({"role": "user", "content": "check leaves"})
#             st.rerun()
# else:
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         if st.button("👤 My Details", use_container_width=True):
#             st.session_state.role_sessions[role]["messages"].append({"role": "user", "content": "show all my details in a format"})
#             st.rerun()
#     with col2:
#         if st.button("📅 Apply Leave", use_container_width=True):
#             st.session_state.role_sessions[role]["messages"].append({"role": "user", "content": "apply leave"})
#             st.rerun()
#     with col3:
#         if st.button("🔄 Start Onboarding", use_container_width=True):
#             st.session_state.role_sessions[role]["messages"].append({"role": "user", "content": "start onboarding"})
#             st.rerun()

# st.markdown("---")
# st.caption(f"Logged in as: **{role.title()}** | Email: {user_email}")



# """
# ui/main.py
# """
# import streamlit as st
# import os
# import sys
# from sqlalchemy import desc

# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
# sys.path.insert(0, parent_dir)

# from db import get_db
# from models import Employee, Onboarding, LeaveRequest
# from rag_pipeline import retriever, llm
# from hr_graph import build_graph

# st.set_page_config(page_title="Office Assistant", layout="centered")

# # --- CSS ---
# st.markdown("""
# <style>
#     .stChatMessage.st-emotion-cache-16idsys.eeusbqq4 { flex-direction: row-reverse; text-align: right; }
#     .stButton button { width: 100%; font-weight: bold; }
# </style>
# """, unsafe_allow_html=True)

# # --- SESSION STATE ---
# if "user_email" not in st.session_state: st.session_state.user_email = None
# if "role" not in st.session_state: st.session_state.role = None
# if "role_sessions" not in st.session_state:
#     st.session_state.role_sessions = {
#         "employee": {"messages": [], "graph_context": {"onboarding_active": False, "leave_draft": {}}},
#         "admin": {"messages": [], "graph_context": {"onboarding_active": False, "leave_draft": {}}}
#     }

# db = next(get_db())

# # ==========================================
# #      LOGIN / SIGNUP SCREEN
# # ==========================================
# if st.session_state.user_email is None:
#     st.title("🏢 Office Assistant Portal")
    
#     tab1, tab2 = st.tabs(["🔑 Login", "📝 New Joiner Signup"])
    
#     # --- LOGIN TAB ---
#     with tab1:
#         email = st.text_input("Email", key="login_email")
#         password = st.text_input("Password", type="password", key="login_pass")
#         if st.button("Login"):
#             user = db.query(Employee).filter(Employee.email == email, Employee.password == password).first()
#             if user:
#                 st.session_state.user_email = user.email
#                 st.session_state.role = user.role
#                 st.rerun()
#             else:
#                 st.error("Invalid Email or Password")

#     # --- SIGNUP TAB ---
#     with tab2:
#         st.caption("New to the company? Sign up here.")
#         new_email = st.text_input("Email", key="signup_email")
#         new_pass = st.text_input("Create Password", type="password", key="signup_pass")
#         new_name = st.text_input("Full Name", key="signup_name")
        
#         if st.button("Sign Up"):
#             if db.query(Employee).filter(Employee.email == new_email).first():
#                 st.error("Email already exists.")
#             else:
#                 # Create user as 'signed_up' (Inactive until Admin triggers)
#                 new_user = Employee(
#                     name=new_name, 
#                     email=new_email, 
#                     password=new_pass, 
#                     role="employee", 
#                     onboarding_status="signed_up" # Step 1 of Manager's Flow
#                 )
#                 db.add(new_user); db.commit()
#                 st.success("Signup Successful! Please wait for Admin to initiate your onboarding.")

# # ==========================================
# #      MAIN CHAT INTERFACE
# # ==========================================
# else:
#     role = st.session_state.role
#     user_email = st.session_state.user_email
    
#     # --- LOGOUT ---
#     with st.sidebar:
#         st.write(f"Role: **{role.title()}**")
#         # st.write(f"User: **{user_email}**")
#         if st.button("Logout"):
#             st.session_state.user_email = None; st.session_state.role = None
#             st.rerun()

#     # --- AUTO-GREETING LOGIC (Manager Point 2.4) ---
#     # If user logs in and status is 'onboarding_triggered', Bot speaks first.
#     current_session = st.session_state.role_sessions[role]
#     user_obj = db.query(Employee).filter(Employee.email == user_email).first()

#     if role == "employee" and user_obj.onboarding_status == "onboarding_triggered" and not current_session["messages"]:
#         intro_msg = f"Hello {user_obj.name}! 👋\nAdmin has initiated your onboarding.\n\n**Shall we start filling your details now?** (Type 'Yes')"
#         current_session["messages"].append({"role": "assistant", "content": intro_msg})

#     # --- CHAT UI ---
#     st.title(f"💬 {role.title()} Chat")
    
#     for msg in current_session["messages"]:
#         avatar = "🤖" if msg["role"] == "assistant" else "🧑‍💻"
#         with st.chat_message(msg["role"], avatar=avatar): st.markdown(msg["content"])

#     user_input = st.chat_input("Type here...")

#     if user_input:
#         current_session["messages"].append({"role": "user", "content": user_input})
#         with st.chat_message("user", avatar="🧑‍💻"): st.markdown(user_input)
        
#         # Build State
#         state = {
#             "message": user_input, "user_id": user_email, "role": role, 
#             "messages": current_session["messages"], "db": db, "retriever": retriever, "llm": llm, "db_user": user_obj,
#             "onboarding_active": current_session["graph_context"].get("onboarding_active", False),
#             "leave_draft": current_session["graph_context"].get("leave_draft", {}),
#             "notification": None
#         }
        
#         graph = build_graph(db, retriever, llm)
#         with st.spinner("Thinking..."):
#             final_state = graph.invoke(state)

#         # Update Session
#         current_session["messages"] = final_state["messages"]
#         current_session["graph_context"]["onboarding_active"] = final_state.get("onboarding_active", False)
#         current_session["graph_context"]["leave_draft"] = final_state.get("leave_draft", {})
        
#         # Toast
#         if final_state.get("notification"): st.toast(final_state["notification"], icon="🔔")
        
#         # Assistant Reply
#         last_msg = final_state["messages"][-1]
#         if last_msg["role"] == "assistant":
#             with st.chat_message("assistant", avatar="🤖"): st.markdown(last_msg["content"])




# version two
# """
# ui/main.py
# """
# import streamlit as st
# import os
# import sys
# from sqlalchemy import desc

# # --- PATH SETUP ---
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
# sys.path.insert(0, parent_dir)

# from db import get_db
# from models import Employee, Onboarding, LeaveRequest
# from rag_pipeline import retriever, llm
# from hr_graph import build_graph

# st.set_page_config(page_title="Office Assistant", layout="centered")

# # --- CSS ---
# st.markdown("""
# <style>
#     .stChatMessage.st-emotion-cache-16idsys.eeusbqq4 { flex-direction: row-reverse; text-align: right; }
#     .stButton button { width: 100%; font-weight: bold; }
#     div[data-testid="stToast"] { padding: 1rem; width: 300px; }
# </style>
# """, unsafe_allow_html=True)

# # --- SESSION STATE SETUP ---
# if "user_email" not in st.session_state: st.session_state.user_email = None
# if "role" not in st.session_state: st.session_state.role = None

# # CRITICAL FIX: Store sessions by EMAIL, not ROLE.
# # Structure: { "email@domain.com": { "messages": [], "graph_context": {...} } }
# if "user_sessions" not in st.session_state:
#     st.session_state.user_sessions = {}

# db = next(get_db())

# # ==========================================
# #      LOGIN / SIGNUP SCREEN
# # ==========================================
# if st.session_state.user_email is None:
#     st.title("🏢 Office Assistant Portal")
    
#     tab1, tab2 = st.tabs(["🔑 Login", "📝 New Joiner Signup"])
    
#     # --- LOGIN TAB ---
#     with tab1:
#         email = st.text_input("Email", key="login_email").strip().lower()
#         password = st.text_input("Password", type="password", key="login_pass")
#         if st.button("Login"):
#             user = db.query(Employee).filter(Employee.email == email, Employee.password == password).first()
#             if user:
#                 st.session_state.user_email = user.email
#                 st.session_state.role = user.role
#                 st.rerun()
#             else:
#                 st.error("Invalid Email or Password")

#     # --- SIGNUP TAB ---
#     with tab2:
#         st.write("") # Spacer
#         st.caption("New to the company? Create your account below.")
        
#         new_email = st.text_input("Email Address", key="signup_email").strip().lower()
#         new_pass = st.text_input("Create Password", type="password", key="signup_pass")
#         new_name = st.text_input("Full Name", key="signup_name")
        
#         if st.button("Create Account"):
#             # 1. Validation Check
#             if not new_email or not new_pass or not new_name:
#                 st.error("⚠️ Please fill in all fields.")
            
#             # 2. Duplicate Check
#             elif db.query(Employee).filter(Employee.email == new_email).first():
#                 st.warning("⚠️ **Account already exists!**\n\nThis email is already registered. Please switch to the **Login** tab.")
            
#             else:
#                 # 3. Create User
#                 new_user = Employee(
#                     name=new_name, 
#                     email=new_email, 
#                     password=new_pass, 
#                     role="employee", 
#                     onboarding_status="signed_up" 
#                 )
#                 db.add(new_user)
#                 db.commit()
#                 st.success("✅ **Signup Successful!**\n\nPlease wait for the Admin to initiate your onboarding. You can try logging in once invited.")

# # ==========================================
# #      MAIN CHAT INTERFACE
# # ==========================================
# else:
#     role = st.session_state.role
#     user_email = st.session_state.user_email
    
#     # --- LOGOUT ---
#     with st.sidebar:
#         st.write(f"User: **{user_email}**")
#         st.write(f"Role: **{role.title()}**")
        
#         if st.button("Logout"):
#             st.session_state.user_email = None
#             st.session_state.role = None
#             st.rerun()
            
#         if st.button("🗑️ Clear Chat"):
#              # Only clear THIS user's chat
#              if user_email in st.session_state.user_sessions:
#                  st.session_state.user_sessions[user_email] = {
#                     "messages": [], 
#                     "graph_context": {"onboarding_active": False, "leave_draft": {}}
#                  }
#                  st.rerun()

#     # --- INITIALIZE USER SESSION IF MISSING ---
#     if user_email not in st.session_state.user_sessions:
#         st.session_state.user_sessions[user_email] = {
#             "messages": [],
#             "graph_context": {"onboarding_active": False, "leave_draft": {}}
#         }
    
#     # LOAD CURRENT USER SESSION
#     current_session = st.session_state.user_sessions[user_email]
    
#     user_obj = db.query(Employee).filter(Employee.email == user_email).first()

#     # --- AUTO-GREETING LOGIC (Manager Point 2.4) ---
#     # If user logs in and status is 'onboarding_triggered', Bot speaks first.
#     if role == "employee" and user_obj.onboarding_status == "onboarding_triggered" and not current_session["messages"]:
#         intro_msg = f"Hello {user_obj.name}! 👋\nAdmin has initiated your onboarding.\n\n**Shall we start filling your details now?** (Type 'Yes')"
#         current_session["messages"].append({"role": "assistant", "content": intro_msg})

#     # --- CHAT UI ---
#     st.title(f"💬 {role.title()} Chat")
    
#     for msg in current_session["messages"]:
#         avatar = "🤖" if msg["role"] == "assistant" else "🧑‍💻"
#         with st.chat_message(msg["role"], avatar=avatar): st.markdown(msg["content"])

#     user_input = st.chat_input("Type here...")

#     if user_input:
#         current_session["messages"].append({"role": "user", "content": user_input})
#         with st.chat_message("user", avatar="🧑‍💻"): st.markdown(user_input)
        
#         # Build State
#         state = {
#             "message": user_input, "user_id": user_email, "role": role, 
#             "messages": current_session["messages"], "db": db, "retriever": retriever, "llm": llm, "db_user": user_obj,
#             "onboarding_active": current_session["graph_context"].get("onboarding_active", False),
#             "leave_draft": current_session["graph_context"].get("leave_draft", {}),
#             "notification": None
#         }
        
#         graph = build_graph(db, retriever, llm)
#         with st.spinner("Thinking..."):
#             final_state = graph.invoke(state)

#         # Update Session
#         current_session["messages"] = final_state["messages"]
#         current_session["graph_context"]["onboarding_active"] = final_state.get("onboarding_active", False)
#         current_session["graph_context"]["leave_draft"] = final_state.get("leave_draft", {})
        
#         # Toast
#         if final_state.get("notification"): st.toast(final_state["notification"], icon="🔔")
        
#         # Assistant Reply
#         last_msg = final_state["messages"][-1]
#         if last_msg["role"] == "assistant":
#             with st.chat_message("assistant", avatar="🤖"): st.markdown(last_msg["content"])




# version one
# """
# ui/main.py
# """
# import streamlit as st
# import os
# import sys
# import re
# from sqlalchemy import desc

# # --- PATH SETUP ---
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
# sys.path.insert(0, parent_dir)

# from db import get_db
# from models import Employee, Onboarding, LeaveRequest
# from rag_pipeline import retriever, llm
# from hr_graph import build_graph

# st.set_page_config(page_title="Office Assistant", layout="centered")

# # --- CSS ---
# st.markdown("""
# <style>
#     .stChatMessage.st-emotion-cache-16idsys.eeusbqq4 { flex-direction: row-reverse; text-align: right; }
#     .stButton button { width: 100%; font-weight: bold; }
#     div[data-testid="stToast"] { padding: 1rem; width: 300px; }
# </style>
# """, unsafe_allow_html=True)

# # --- SESSION STATE SETUP ---
# if "user_email" not in st.session_state: st.session_state.user_email = None
# if "role" not in st.session_state: st.session_state.role = None
# if "user_sessions" not in st.session_state: st.session_state.user_sessions = {}
# if "greeted" not in st.session_state: st.session_state.greeted = False

# # Flag to prevent double-greeting on reruns
# if "notification_checked" not in st.session_state: st.session_state.notification_checked = False

# db = next(get_db())

# # --- VALIDATION HELPERS ---
# def validate_mobile(number):
#     return bool(re.match(r"^[6-9]\d{9}$", number))

# def validate_pan(pan):
#     return bool(re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]$", pan))

# def validate_aadhaar(aadhaar):
#     return bool(re.match(r"^\d{12}$", aadhaar))

# # ==========================================
# #      LOGIN / SIGNUP SCREEN
# # ==========================================
# if st.session_state.user_email is None:
#     st.title("🏢 VOLTA HR Portal")
#     st.info("Welcome. Please log in with the credentials provided by your HR Admin.")
    
#     with st.container():
#         email = st.text_input("Email", key="login_email").strip().lower()
#         password = st.text_input("Password", type="password", key="login_pass")
        
#         if st.button("Login", type="primary"):
#             user = db.query(Employee).filter(Employee.email == email, Employee.password == password).first()
#             if user:
#                 st.session_state.user_email = user.email
#                 st.session_state.role = user.role
#                 st.toast(f"Welcome back, {user.name}!", icon="👋")
#                 st.session_state.greeted = False # Ensure bot greets them after login
#                 st.rerun()
#             else:
#                 st.error("❌ Invalid Credentials. If you are a new joiner, please check your email for your login details.")


# # ==========================================
# #      MAIN INTERFACE
# # ==========================================
# else:
#     role = st.session_state.role
#     user_email = st.session_state.user_email
    
#     # --- SIDEBAR ---
#     with st.sidebar:
#         st.write(f"👤 **{user_email}**")
#         st.write(f"🛠️ Role: **{role.title()}**")
#         st.markdown("---")
        
#         if st.button("🗑️ Clear My Chat"):
#              if user_email in st.session_state.user_sessions:
#                  st.session_state.user_sessions[user_email] = {
#                     "messages": [], "graph_context": {"onboarding_active": False, "leave_draft": {}}
#                  }
#                  st.session_state.notification_checked = False
#                  st.rerun()

#         if st.button("🚪 Logout"):
#             st.session_state.user_email = None
#             st.session_state.role = None
#             st.rerun()

#     # Load User & Session
#     if user_email not in st.session_state.user_sessions:
#         st.session_state.user_sessions[user_email] = {
#             "messages": [], "graph_context": {"onboarding_active": False, "leave_draft": {}}
#         }
#     current_session = st.session_state.user_sessions[user_email]
#     user_obj = db.query(Employee).filter(Employee.email == user_email).first()

#     # --- PROACTIVE GREETING TRIGGER in ui/main.py ---
#     if not st.session_state.get("greeted", False) and user_obj.onboarding_status == "active":
#         initial_state = {
#             "message": "hi", # Sending 'hi' triggers the notification logic in hr_rag_node
#             "user_id": user_email, 
#             "role": role, 
#             "messages": current_session["messages"], 
#             "db": db, 
#             "retriever": retriever, 
#             "llm": llm, 
#             "db_user": user_obj, # Pass the full user object
#             "onboarding_active": False,
#             "leave_draft": {},
#             "notification": None
#         }
        
#         graph = build_graph(db, retriever, llm)
#         with st.spinner("Syncing dashboard..."):
#             final_state = graph.invoke(initial_state)
#             current_session["messages"] = final_state["messages"]
#             st.session_state.greeted = True
#             st.rerun()

#     # =========================================================
#     #  SCENARIO A: ONBOARDING FORM (UPDATED)
#     # =========================================================
#     if role == "employee" and user_obj.onboarding_status == "onboarding_triggered":
#         st.title("📝 Complete Your Profile")
#         st.info(f"👋 Welcome {user_obj.name}! Please setup your profile to generate your Employee ID.")
        
#         with st.form("onboarding_form"):
#             st.subheader("Personal Details")
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 f_name = st.text_input("Full Name", value=user_obj.name)
#                 f_age = st.number_input("Age", min_value=18, max_value=100, step=1)
#                 f_dob = st.date_input("Date of Birth")
#                 f_nationality = st.text_input("Nationality", value="Indian")
#                 f_mobile = st.text_input("Mobile Number (10 digits)")
                
#             with col2:
#                 f_blood = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
#                 f_marital = st.selectbox("Marital Status", ["Single", "Married", "Divorced"])
#                 f_state = st.selectbox("State", ["Telangana", "Andhra Pradesh", "Karnataka", "Maharashtra", "Tamil Nadu", "Delhi", "Other"])
#                 f_aadhaar = st.text_input("Aadhaar Number (12 digits)")
#                 f_pan = st.text_input("PAN Card (e.g., ABCDE1234F)")

#             st.subheader("Address")
#             f_address = st.text_area("Permanent Address", placeholder="#123, Street Name, City, Pincode")

#             st.markdown("---")
#             f_agree = st.checkbox("✅ I hereby declare that the information provided above is true.")
            
#             submit_btn = st.form_submit_button("Submit Details")

#             if submit_btn:
#                 # --- VALIDATION LOGIC ---
#                 errors = []
#                 if not validate_mobile(f_mobile): errors.append("❌ Invalid Mobile Number")
#                 if not validate_aadhaar(f_aadhaar): errors.append("❌ Invalid Aadhaar Number")
#                 if not validate_pan(f_pan): errors.append("❌ Invalid PAN Format")
#                 if len(f_address) < 10: errors.append("❌ Address is too short")
#                 if not f_agree: errors.append("⚠️ You must accept the declaration.")
                
#                 if errors:
#                     for e in errors: st.error(e)
#                 else:
#                     # --- SAVE TO DB ---
#                     data_blob = (
#                         f"Name: {f_name}\n"
#                         f"Age: {f_age}\n"
#                         f"DOB: {f_dob}\n"
#                         f"Nationality: {f_nationality}\n"
#                         f"Address: {f_address}\n"
#                         f"Mobile: {f_mobile}\n"
#                         f"Blood Group: {f_blood}\n"
#                         f"State: {f_state}\n"
#                         f"Marital Status: {f_marital}\n"
#                         f"Aadhaar: {f_aadhaar}\n"
#                         f"PAN: {f_pan}\n"
#                         f"Agreement Signed: Yes"
#                     )
                    
#                     onboard_record = db.query(Onboarding).filter(Onboarding.employee_id == user_obj.id).first()
#                     if not onboard_record:
#                         onboard_record = Onboarding(employee_id=user_obj.id, step=5, data=data_blob, completed=False)
#                         db.add(onboard_record)
#                     else:
#                         onboard_record.data = data_blob
                    
#                     user_obj.onboarding_status = "details_submitted"
#                     db.commit()
                    
#                     st.success("✅ Details Submitted Successfully! Waiting for Admin approval.")
#                     st.rerun()

#     # =========================================================
#     #  SCENARIO B: WAITING FOR APPROVAL
#     # =========================================================
#     elif role == "employee" and user_obj.onboarding_status == "details_submitted":
#         st.title("⏳ Application Under Review")
#         st.success("You have successfully submitted your details.")
#         st.write("Your profile is currently being reviewed by the HR Admin. You will receive an email once your Employee ID is generated.")

#     # =========================================================
#     #  SCENARIO C: REGULAR CHAT
#     # =========================================================
#     else:
#         st.title(f"💬 {role.title()} Assistant")
        
#         for msg in current_session["messages"]:
#             avatar = "🤖" if msg["role"] == "assistant" else "🧑‍💻"
#             with st.chat_message(msg["role"], avatar=avatar): st.markdown(msg["content"])

#         user_input = st.chat_input("Type here...")

#         if user_input:
#             current_session["messages"].append({"role": "user", "content": user_input})
#             with st.chat_message("user", avatar="🧑‍💻"): st.markdown(user_input)
            
#             # Build State
#             state = {
#                 "message": user_input, "user_id": user_email, "role": role, 
#                 "messages": current_session["messages"], "db": db, "retriever": retriever, "llm": llm, "db_user": user_obj,
#                 "onboarding_active": current_session["graph_context"].get("onboarding_active", False),
#                 "leave_draft": current_session["graph_context"].get("leave_draft", {}),
#                 "notification": None
#             }
            
#             graph = build_graph(db, retriever, llm)
#             with st.spinner("Thinking..."):
#                 final_state = graph.invoke(state)

#             current_session["messages"] = final_state["messages"]
#             current_session["graph_context"]["onboarding_active"] = final_state.get("onboarding_active", False)
#             current_session["graph_context"]["leave_draft"] = final_state.get("leave_draft", {})
            
#             if final_state.get("notification"): st.toast(final_state["notification"], icon="🔔")
            
#             last_msg = final_state["messages"][-1]
#             if last_msg["role"] == "assistant":
#                 with st.chat_message("assistant", avatar="🤖"): st.markdown(last_msg["content"])





#VERSION ZERO (BEFORE REFACTOR)
# """
# ui/main.py
# """
# import streamlit as st
# import os
# import sys
# import time
# from sqlalchemy import desc

# # --- PATH SETUP ---
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
# sys.path.insert(0, parent_dir)

# from db import get_db, engine, Base, SessionLocal
# from models import Employee, Onboarding, LeaveRequest
# from rag_pipeline import retriever, llm
# from hr_graph import build_graph


# # ==========================================
# #  🛠️ AUTO-SETUP (Critical: Run First)
# # ==========================================
# def initialize_system():
#     """Forces table creation and Admin user generation on startup."""
#     try:
#         # 1. Create All Tables
#         Base.metadata.create_all(bind=engine)
        
#         # 2. Check & Create Admin
#         db = SessionLocal()
#         admin_email = "bharathkumarking143@gmail.com"
        
#         # Use a safe query to check if admin exists
#         try:
#             existing_admin = db.query(Employee).filter(Employee.email == admin_email).first()
#             if not existing_admin:
#                 admin = Employee(
#                     name="Bharath Admin",
#                     email=admin_email,
#                     password="Admin",  # Password from your error log
#                     role="admin",
#                     onboarding_status="active"
#                 )
#                 db.add(admin)
#                 db.commit()
#                 print(f"✅ AUTO-SETUP: Admin {admin_email} created.")
#             else:
#                 print("✅ AUTO-SETUP: Admin already exists.")
#         except Exception as e:
#              print(f"⚠️ AUTO-SETUP Query Error: {e}")
             
#         db.close()
#     except Exception as e:
#         print(f"⚠️ AUTO-SETUP Critical Error: {e}")

# # 🔥 CALL THIS IMMEDIATELY
# initialize_system()



# st.set_page_config(page_title="Office Assistant", layout="centered")

# # --- CSS ---
# st.markdown("""
# <style>
#     .stChatMessage.st-emotion-cache-16idsys.eeusbqq4 { flex-direction: row-reverse; text-align: right; }
#     .stButton button { width: 100%; font-weight: bold; }
# </style>
# """, unsafe_allow_html=True)

# # --- SESSION STATE ---
# if "user_email" not in st.session_state: st.session_state.user_email = None
# if "role" not in st.session_state: st.session_state.role = None
# if "user_sessions" not in st.session_state: st.session_state.user_sessions = {}
# if "notification_checked" not in st.session_state: st.session_state.notification_checked = False

# # Initialize polling state
# if "last_notif_check" not in st.session_state:
#     st.session_state.last_notif_check = {
#         "admin_pending_count": 0,
#         "emp_last_leave_id": None,
#         "last_poll_time": time.time()
#     }

# # db = next(get_db())

# # ==========================================
# #      LOGIN SCREEN
# # ==========================================
# if st.session_state.user_email is None:
#     st.title("🏢 VOLTA HR Portal")
#     st.info("Welcome. Please log in with the credentials provided by your HR Admin.")
    
#     with st.container():
#         email = st.text_input("Email", key="login_email").strip().lower()
#         password = st.text_input("Password", type="password", key="login_pass")
#         if st.button("Login", type="primary"):
#             user = db.query(Employee).filter(Employee.email == email, Employee.password == password).first()
#             if user:
#                 st.session_state.user_email = user.email
#                 st.session_state.role = user.role
#                 st.session_state.notification_checked = False 
#                 st.rerun()
#             else:
#                 st.error("❌ Invalid Credentials.")

# # ==========================================
# #      MAIN INTERFACE
# # ==========================================
# else:
#     # Get a fresh DB session for the main app
#     db = next(get_db())


#     role = st.session_state.role
#     user_email = st.session_state.user_email

#     # 1. FETCH USER DETAILS FIRST (Moved Up)
#     user_obj = db.query(Employee).filter(Employee.email == user_email).first()
#     display_name = user_obj.name if user_obj else user_email
    
#     # --- SIDEBAR ---
#     with st.sidebar:
#         st.write(f"👤 **{display_name}**")
#         st.write(f"🛠️ Role: **{role.title()}**")
        
#         if st.button("🗑️ Clear My Chat"):
#              if user_email in st.session_state.user_sessions:
#                  st.session_state.user_sessions[user_email] = {
#                     "messages": [], "graph_context": {"onboarding_active": False, "leave_draft": {}}
#                  }
#                  st.session_state.notification_checked = False
#                  st.rerun()

#         if st.button("🚪 Logout"):
#             st.session_state.user_email = None
#             st.session_state.role = None
#             st.rerun()

#     # Load Session
#     if user_email not in st.session_state.user_sessions:
#         st.session_state.user_sessions[user_email] = {
#             "messages": [], "graph_context": {"onboarding_active": False, "leave_draft": {}}
#         }
#     current_session = st.session_state.user_sessions[user_email]
#     user_obj = db.query(Employee).filter(Employee.email == user_email).first()

#     # =========================================================
#     #  🔄 NOTIFICATION LOGIC (FIXED)
#     # =========================================================
#     @st.fragment(run_every=3)
#     def poll_notifications():
#         if not st.session_state.user_email: return
#         local_db = next(get_db())
        
#         # --- ADMIN CHECK ---
#         if role == "admin":
#             p_leave = local_db.query(LeaveRequest).filter(LeaveRequest.status == "pending_approval").count()
#             p_onboard = local_db.query(Employee).filter(Employee.onboarding_status == "details_submitted").count()
#             current_total = p_leave + p_onboard
#             last_total = st.session_state.last_notif_check["admin_pending_count"]
            
#             # A. Welcome Message (Runs once)
#             if not st.session_state.notification_checked:
#                 st.session_state.notification_checked = True
#                 # FIX: Sync the counter HERE so we don't trigger the alert immediately after
#                 st.session_state.last_notif_check["admin_pending_count"] = current_total
                
#                 if current_total > 0:
#                     msg = f"👋 **Welcome Admin!**\nUpdates: {p_leave} Leave, {p_onboard} Onboarding pending.\nType **'show pending requests'**."
#                 else:
#                     msg = "👋 **Welcome Admin!** All systems operational. No pending requests."

#                 current_session["messages"].append({"role": "assistant", "content": msg})

#                 time.sleep(1)
#                 st.rerun()

#             # B. New Alert (Runs on change)
#             elif current_total > last_total:
#                 st.session_state.last_notif_check["admin_pending_count"] = current_total # Update state first
#                 new_count = current_total - last_total

#                 st.toast(f"🔔 {new_count} New Request(s)!", icon="🔔")
#                 current_session["messages"].append({"role": "assistant", "content": f"🔔 **New Request Received!**\nTotal Pending: {current_total}\nType **'show pending requests'**."})
#                 time.sleep(2)
#                 st.rerun()
            
#             # Sync if count decreased (approved/rejected)
#             if current_total != last_total:
#                 st.session_state.last_notif_check["admin_pending_count"] = current_total

#         # --- EMPLOYEE CHECK ---
#         elif role == "employee":
#             last_leave = local_db.query(LeaveRequest).filter(
#                 LeaveRequest.employee_id == user_obj.id, 
#                 LeaveRequest.notification_seen == False
#             ).order_by(desc(LeaveRequest.created_at)).first()
            
#             # A. Welcome Message (Runs once)
#             if not st.session_state.notification_checked:
#                 st.session_state.notification_checked = True
                
#                 # Check for updates to include in welcome
#                 if last_leave and last_leave.status in ["approved", "rejected"]:
#                     icon = "✅" if last_leave.status == "approved" else "❌"
#                     msg = f"👋 **Hi {user_obj.name}!**\n\n{icon} **Update:** Your leave for **{last_leave.start_date.date()}** was **{last_leave.status.upper()}**."
#                     last_leave.notification_seen = True
#                     local_db.commit()
#                 else:
#                     msg = f"👋 **Hi {user_obj.name}!** I'm ready to solve your queries."
                
#                 current_session["messages"].append({"role": "assistant", "content": msg})

#                 time.sleep(1)
#                 st.rerun()

#             # B. Live Updates
#             elif last_leave and last_leave.status in ["approved", "rejected"]:
#                 last_leave.notification_seen = True
#                 local_db.commit()
                
#                 icon = "✅" if last_leave.status == "approved" else "❌"
#                 msg = f"{icon} **Update:** Your leave for **{last_leave.start_date.date()}** was **{last_leave.status.upper()}**."
                
#                 st.toast(f"Leave {last_leave.status.title()}!", icon=icon)
#                 current_session["messages"].append({"role": "assistant", "content": msg})
#                 time.sleep(2)
#                 st.rerun()

#     # Run the poller
#     poll_notifications()
    
#     # =========================================================
#     #  SCENARIO A: ONBOARDING FORM
#     # =========================================================
#     if role == "employee" and user_obj.onboarding_status == "onboarding_triggered":
#         st.title("📝 Complete Your Profile")
#         with st.form("onboarding_form"):
#             col1, col2 = st.columns(2)
#             with col1:
#                 f_name = st.text_input("Full Name", value=user_obj.name)
#                 f_age = st.number_input("Age", 18, 100)
#                 f_dob = st.date_input("Date of Birth")
#                 f_nationality = st.text_input("Nationality", value="Indian")
#                 f_mobile = st.text_input("Mobile Number")
#             with col2:
#                 f_blood = st.selectbox("Blood Group", ["O+", "A+", "B+", "AB+"])
#                 f_marital = st.selectbox("Marital Status", ["Single", "Married"])
#                 f_state = st.selectbox("State", ["Telangana", "Andhra Pradesh", "Other"])
#                 f_aadhaar = st.text_input("Aadhaar Number")
#                 f_pan = st.text_input("PAN Card")
#             f_address = st.text_area("Address")
#             f_agree = st.checkbox("✅ I declare the above information is true.")
            
#             if st.form_submit_button("Submit Details"):
#                 if f_agree and len(f_mobile) >= 10:
#                     data_blob = f"Name: {f_name}\nMobile: {f_mobile}\nDOB: {f_dob}\nAddress: {f_address}\nPAN: {f_pan}\nAadhaar: {f_aadhaar}"
#                     onboard_record = db.query(Onboarding).filter(Onboarding.employee_id == user_obj.id).first()
#                     if not onboard_record:
#                         onboard_record = Onboarding(employee_id=user_obj.id, step=5, data=data_blob, completed=False)
#                         db.add(onboard_record)
#                     else:
#                         onboard_record.data = data_blob
#                     user_obj.onboarding_status = "details_submitted"
#                     db.commit()
#                     st.success("✅ Submitted! HR will review shortly.")
#                     st.rerun()
#                 else:
#                     st.error("⚠️ Please fill all valid details and accept the declaration.")

#     # =========================================================
#     #  SCENARIO B: WAITING
#     # =========================================================
#     elif role == "employee" and user_obj.onboarding_status == "details_submitted":
#         st.title("⏳ Under Review")
#         st.info("Your details are being reviewed by Admin.")

#     # =========================================================
#     #  SCENARIO C: CHAT
#     # =========================================================
#     else:
#         st.title(f"💬 {role.title()} Assistant")
        
#         for msg in current_session["messages"]:
#             avatar = "🤖" if msg["role"] == "assistant" else "🧑‍💻"
#             with st.chat_message(msg["role"], avatar=avatar): st.markdown(msg["content"])

#         if user_input := st.chat_input("Type here..."):
#             current_session["messages"].append({"role": "user", "content": user_input})
#             with st.chat_message("user", avatar="🧑‍💻"): st.markdown(user_input)
            
#             state = {
#                 "message": user_input, "user_id": user_email, "role": role, 
#                 "messages": current_session["messages"], "db": db, "retriever": retriever, "llm": llm, "db_user": user_obj,
#                 "onboarding_active": current_session["graph_context"].get("onboarding_active", False),
#                 "leave_draft": current_session["graph_context"].get("leave_draft", {}),
#                 "notification": None
#             }
            
#             graph = build_graph(db, retriever, llm)
#             with st.status("🤖 **Agent is thinking...**", expanded=True) as status:
#                 st.write("🔄 Analyzing user intent...")
#                 final_state = graph.invoke(state)
                
#                 # Dynamic Status Labels
#                 intent = final_state.get("intent", "unknown")
#                 if intent == "leave": st.write("🗓️ Accessing Leave Module...")
#                 elif intent == "admin_onboarding": st.write("🔐 Checking Admin Database...")
#                 elif intent == "hr_query": st.write("📚 Searching Employee Handbook...")
                
#                 status.update(label="✅ Response Ready", state="complete", expanded=False)

#             current_session["messages"] = final_state["messages"]
#             current_session["graph_context"]["onboarding_active"] = final_state.get("onboarding_active", False)
#             current_session["graph_context"]["leave_draft"] = final_state.get("leave_draft", {})
            
#             if final_state.get("notification"): 
#                 st.toast(final_state["notification"], icon="🔔")
#                 time.sleep(1) # Small delay for action toast
            
#             last_msg = final_state["messages"][-1]
#             if last_msg["role"] == "assistant":
#                 with st.chat_message("assistant", avatar="🤖"): st.markdown(last_msg["content"])
            
#             st.rerun()




"""
ui/main.py
"""
import streamlit as st
import os
import sys
import time
from sqlalchemy import desc, inspect

# --- PATH SETUP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, parent_dir)

# --- IMPORTS ---
from db import get_db, engine, Base, SessionLocal
# We delay importing models slightly to ensure Base is ready, 
# but we MUST import them for create_all to work.
import models 
from models import Employee, Onboarding, LeaveRequest
from rag_pipeline import retriever, llm
from hr_graph import build_graph

# ==========================================
#  🛠️ CRITICAL: AUTO-SETUP (Self-Healing)
# ==========================================
def initialize_system():
    """Forces table creation and Admin user generation on startup."""
    print("⚡ INITIALIZING DATABASE SYSTEM...")
    try:
        # 1. DEBUG: Check if models are registered
        print(f"🔍 DEBUG: Tables found in metadata: {list(Base.metadata.tables.keys())}")
        
        if not Base.metadata.tables:
            print("⚠️ CRITICAL WARNING: No tables found in metadata! Models might not be imported correctly.")

        # 2. Force Create All Tables
        Base.metadata.create_all(bind=engine)
        print("✅ TABLES CREATION STEP COMPLETED")
        
        # 3. Verify Creation using Inspector
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        print(f"🔍 DEBUG: Tables actually in DB: {existing_tables}")

        if "employees" not in existing_tables:
            print("❌ ERROR: 'employees' table still missing after creation attempt.")
            return

        # 4. Create Admin User
        db = SessionLocal()
        admin_email = os.getenv("SENDER_EMAIL") # <--- YOUR EMAIL
        
        # Now it is safe to query because we verified the table exists
        existing_admin = db.query(Employee).filter(Employee.email == admin_email).first()
        
        if not existing_admin:
            admin = Employee(
                name="Bharath Admin",
                email=admin_email,
                password="Admin", 
                role="admin",
                onboarding_status="active"
            )
            db.add(admin)
            db.commit()
            print(f"✅ ADMIN USER CREATED: {admin_email}")
        else:
            print("✅ Admin user already exists.")
        
        db.close()
    except Exception as e:
        print(f"⚠️ SETUP EXCEPTION: {e}")

# 🔥 CALL THIS IMMEDIATELY
initialize_system()

# ==========================================
#  APP CONFIG
# ==========================================
st.set_page_config(page_title="Office Assistant", layout="centered")

st.markdown("""
<style>
    .stChatMessage.st-emotion-cache-16idsys.eeusbqq4 { flex-direction: row-reverse; text-align: right; }
    .stButton button { width: 100%; font-weight: bold; }
    div[data-testid="stToast"] { padding: 1rem; width: 300px; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "user_email" not in st.session_state: st.session_state.user_email = None
if "role" not in st.session_state: st.session_state.role = None
if "user_sessions" not in st.session_state: st.session_state.user_sessions = {}
if "notification_checked" not in st.session_state: st.session_state.notification_checked = False

if "last_notif_check" not in st.session_state:
    st.session_state.last_notif_check = {
        "admin_pending_count": 0,
        "emp_last_leave_id": None,
        "last_poll_time": time.time()
    }

# ==========================================
#      LOGIN SCREEN
# ==========================================
if st.session_state.user_email is None:
    st.title("🏢 VOLTA HR Portal")
    st.info("Log in with your Admin credentials.")
    
    with st.container():
        email = st.text_input("Email", key="login_email").strip().lower()
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login", type="primary"):
            # Use a fresh session for login
            try:
                login_db = SessionLocal()
                user = login_db.query(Employee).filter(Employee.email == email, Employee.password == password).first()
                login_db.close()
                
                if user:
                    st.session_state.user_email = user.email
                    st.session_state.role = user.role
                    st.session_state.notification_checked = False 
                    st.rerun()
                else:
                    st.error("❌ Invalid Credentials.")
            except Exception as e:
                st.error(f"Login Error: {e}")


# ==========================================
#      MAIN INTERFACE
# ==========================================
else:
    # Use a fresh session for the main app logic
    db = SessionLocal()
    
    try:
        role = st.session_state.role
        user_email = st.session_state.user_email

        # 1. FETCH USER DETAILS
        user_obj = db.query(Employee).filter(Employee.email == user_email).first()

        # 🛡️ AUTO-REFRESH FIX: 
        # If DB says "active" but Session thought "details_submitted", RERUN immediately.
        if user_obj and user_obj.onboarding_status == "active" and st.session_state.get("last_status") != "active":
             st.session_state["last_status"] = "active"
             st.rerun() # <--- This forces the page to reload and show the Chat Interface

        display_name = user_obj.name if user_obj else user_email
        
        # --- SIDEBAR ---
        with st.sidebar:
            st.write(f"👤 **{display_name}**")
            st.write(f"🛠️ Role: **{role.title()}**")
            
            if st.button("🗑️ Clear My Chat"):
                 if user_email in st.session_state.user_sessions:
                     st.session_state.user_sessions[user_email] = {
                        "messages": [], "graph_context": {"onboarding_active": False, "leave_draft": {}}
                     }
                     st.session_state.notification_checked = False
                     st.rerun()

            if st.button("🚪 Logout"):
                st.session_state.user_email = None
                st.session_state.role = None
                st.rerun()

        # Load Session
        if user_email not in st.session_state.user_sessions:
            st.session_state.user_sessions[user_email] = {
                "messages": [], "graph_context": {"onboarding_active": False, "leave_draft": {}}
            }
        current_session = st.session_state.user_sessions[user_email]

        # =========================================================
        #  🔄 NOTIFICATION LOGIC
        # =========================================================
        @st.fragment(run_every=3)
        def poll_notifications():
            if not st.session_state.user_email: return
            local_db = SessionLocal()
            try:
                # --- ADMIN CHECK ---
                if role == "admin":
                    p_leave = local_db.query(LeaveRequest).filter(LeaveRequest.status == "pending_approval").count()
                    p_onboard = local_db.query(Employee).filter(Employee.onboarding_status == "details_submitted").count()
                    current_total = p_leave + p_onboard
                    last_total = st.session_state.last_notif_check["admin_pending_count"]
                    
                    if not st.session_state.notification_checked:
                        st.session_state.notification_checked = True
                        st.session_state.last_notif_check["admin_pending_count"] = current_total
                        
                        if current_total > 0:
                            msg = f"👋 **Welcome Admin!**\nUpdates: {p_leave} Leave, {p_onboard} Onboarding pending.\nType **'show pending requests'**."
                        else:
                            msg = "👋 **Welcome Admin!** All systems operational. No pending requests."

                        current_session["messages"].append({"role": "assistant", "content": msg})
                        time.sleep(1)
                        st.rerun()

                    elif current_total > last_total:
                        st.session_state.last_notif_check["admin_pending_count"] = current_total 
                        new_count = current_total - last_total
                        st.toast(f"🔔 {new_count} New Request(s)!", icon="🔔")
                        current_session["messages"].append({"role": "assistant", "content": f"🔔 **New Request Received!**\nTotal Pending: {current_total}\nType **'show pending requests'**."})
                        time.sleep(2)
                        st.rerun()
                    
                    if current_total != last_total:
                        st.session_state.last_notif_check["admin_pending_count"] = current_total

                # --- EMPLOYEE CHECK ---
                elif role == "employee":
                    last_leave = local_db.query(LeaveRequest).filter(
                        LeaveRequest.employee_id == user_obj.id, 
                        LeaveRequest.notification_seen == False
                    ).order_by(desc(LeaveRequest.created_at)).first()
                    
                    if not st.session_state.notification_checked:
                        st.session_state.notification_checked = True
                        if last_leave and last_leave.status in ["approved", "rejected"]:
                            icon = "✅" if last_leave.status == "approved" else "❌"
                            msg = f"👋 **Hi {user_obj.name}!**\n\n{icon} **Update:** Your leave for **{last_leave.start_date.date()}** was **{last_leave.status.upper()}**."
                            last_leave.notification_seen = True
                            local_db.commit()
                        else:
                            msg = f"👋 **Hi {user_obj.name}!** I'm ready to solve your queries."
                        
                        current_session["messages"].append({"role": "assistant", "content": msg})
                        time.sleep(1)
                        st.rerun()

                    elif last_leave and last_leave.status in ["approved", "rejected"]:
                        last_leave.notification_seen = True
                        local_db.commit()
                        icon = "✅" if last_leave.status == "approved" else "❌"
                        msg = f"{icon} **Update:** Your leave for **{last_leave.start_date.date()}** was **{last_leave.status.upper()}**."
                        st.toast(f"Leave {last_leave.status.title()}!", icon=icon)
                        current_session["messages"].append({"role": "assistant", "content": msg})
                        time.sleep(2)
                        st.rerun()
            finally:
                local_db.close()

        poll_notifications()
        
        # =========================================================
        #  SCENARIO A: ONBOARDING FORM
        # =========================================================
        if role == "employee" and user_obj.onboarding_status == "onboarding_triggered":
            st.title("📝 Complete Your Profile")
            with st.form("onboarding_form"):
                col1, col2 = st.columns(2)
                with col1:
                    f_name = st.text_input("Full Name", value=user_obj.name)
                    f_age = st.number_input("Age", 18, 100)
                    f_dob = st.date_input("Date of Birth")
                    f_nationality = st.text_input("Nationality", value="Indian")
                    f_mobile = st.text_input("Mobile Number")
                with col2:
                    f_blood = st.selectbox("Blood Group", ["O+", "A+", "B+", "AB+"])
                    f_marital = st.selectbox("Marital Status", ["Single", "Married"])
                    f_state = st.selectbox("State", ["Telangana", "Andhra Pradesh", "Other"])
                    f_aadhaar = st.text_input("Aadhaar Number")
                    f_pan = st.text_input("PAN Card")
                f_address = st.text_area("Address")
                f_agree = st.checkbox("✅ I declare the above information is true.")
                
                if st.form_submit_button("Submit Details"):
                    if f_agree and len(f_mobile) >= 10:
                        data_blob = f"Name: {f_name}\nMobile: {f_mobile}\nDOB: {f_dob}\nAddress: {f_address}\nPAN: {f_pan}\nAadhaar: {f_aadhaar}"
                        onboard_record = db.query(Onboarding).filter(Onboarding.employee_id == user_obj.id).first()
                        if not onboard_record:
                            onboard_record = Onboarding(employee_id=user_obj.id, step=5, data=data_blob, completed=False)
                            db.add(onboard_record)
                        else:
                            onboard_record.data = data_blob
                        user_obj.onboarding_status = "details_submitted"
                        db.commit()
                        st.success("✅ Submitted! HR will review shortly.")
                        st.rerun()
                    else:
                        st.error("⚠️ Please fill all valid details and accept the declaration.")

        # =========================================================
        #  SCENARIO B: WAITING
        # =========================================================
        elif role == "employee" and user_obj.onboarding_status == "details_submitted":
            st.title("⏳ Under Review")
            st.info("Your details are being reviewed by Admin.")

        # =========================================================
        #  SCENARIO C: CHAT
        # =========================================================
        else:
            st.title(f"💬 {role.title()} Assistant")
            
            for msg in current_session["messages"]:
                avatar = "🤖" if msg["role"] == "assistant" else "🧑‍💻"
                with st.chat_message(msg["role"], avatar=avatar): st.markdown(msg["content"])

            if user_input := st.chat_input("Type here..."):
                current_session["messages"].append({"role": "user", "content": user_input})
                with st.chat_message("user", avatar="🧑‍💻"): st.markdown(user_input)
                
                state = {
                    "message": user_input, "user_id": user_email, "role": role, 
                    "messages": current_session["messages"], "db": db, "retriever": retriever, "llm": llm, "db_user": user_obj,
                    "onboarding_active": current_session["graph_context"].get("onboarding_active", False),
                    "leave_draft": current_session["graph_context"].get("leave_draft", {}),
                    "notification": None
                }
                
                graph = build_graph(db, retriever, llm)
                with st.status("🤖 **Agent is thinking...**", expanded=True) as status:
                    st.write("🔄 Analyzing user intent...")
                    final_state = graph.invoke(state)
                    
                    intent = final_state.get("intent", "unknown")
                    if intent == "leave": st.write("🗓️ Accessing Leave Module...")
                    elif intent == "admin_onboarding": st.write("🔐 Checking Admin Database...")
                    elif intent == "hr_query": st.write("📚 Searching Employee Handbook...")
                    
                    status.update(label="✅ Response Ready", state="complete", expanded=False)

                current_session["messages"] = final_state["messages"]
                current_session["graph_context"]["onboarding_active"] = final_state.get("onboarding_active", False)
                current_session["graph_context"]["leave_draft"] = final_state.get("leave_draft", {})
                
                if final_state.get("notification"): 
                    st.toast(final_state["notification"], icon="🔔")
                    time.sleep(1) # Small delay for action toast
                
                last_msg = final_state["messages"][-1]
                if last_msg["role"] == "assistant":
                    with st.chat_message("assistant", avatar="🤖"): st.markdown(last_msg["content"])
                
                st.rerun()
    finally:
        # ALWAYS CLOSE THE DB SESSION TO PREVENT LEAKS
        db.close()