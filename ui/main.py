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

# ==========================================
# 1. APP CONFIG (MUST BE FIRST)
# ==========================================
st.set_page_config(page_title="Office Assistant", layout="centered")

# ==========================================
# 2. INSTANT UI CSS (MUST BE SECOND)
# ==========================================
def remove_fading_animations():
    st.markdown("""
        <style>
            /* 1. FORCE INSTANT TRANSITIONS - No Fading */
            .stApp, .stApp * {
                transition: none !important;
                animation: none !important;
                animation-duration: 0s !important;
                transition-duration: 0s !important;
            }
            
            /* 2. Stop page dimming during reruns */
            div[data-testid="stAppViewContainer"], 
            div[data-testid="stMainBlockContainer"],
            div[data-testid="stMain"] {
                opacity: 1 !important;
                filter: none !important;
                transition: none !important;
            }
            
            /* 3. Fix input boxes */
            textarea[disabled], input[disabled] {
                opacity: 1 !important;
                background-color: transparent !important;
                color: inherit !important;
                cursor: default !important;
                border-color: rgba(250, 250, 250, 0.2) !important;
            }
            
            /* 4. Ensure alerts/messages are visible */
            div[data-testid="stAlert"] {
                visibility: visible !important;
                opacity: 1 !important;
                display: flex !important;
            }
            
            /* 5. CRITICAL: Force immediate visibility changes */
            .element-container, .stMarkdown, .stForm {
                transition: none !important;
                animation: none !important;
            }
            
            /* 6. Stop Streamlit's default fade-in effect */
            @keyframes fadeIn {
                from { opacity: 1; }
                to { opacity: 1; }
            }
            
            /* 7. NUCLEAR OPTION - Kill ALL transitions */
            * {
                -webkit-transition: none !important;
                -moz-transition: none !important;
                -o-transition: none !important;
                transition: none !important;
            }
            
            /* 8. Force instant opacity */
            .stApp > div {
                opacity: 1 !important;
            }
            
            /* 9. Prevent container fading */
            .block-container {
                opacity: 1 !important;
                transition: none !important;
            }
            
            /* 10. Override rerun animation */
            .stApp[data-test-script-state="running"] {
                opacity: 1 !important;
            }
        </style>
    """, unsafe_allow_html=True)

# ⚡ EXECUTE CSS IMMEDIATELY (Before DB Connection)
remove_fading_animations()

# --- PATH SETUP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, parent_dir)

# --- IMPORTS ---
from db import get_db, engine, Base, SessionLocal
import models 
from models import Employee, Onboarding, LeaveRequest
from rag_pipeline import retriever, llm
from hr_graph import build_graph

# ==========================================
# 3. ⚡ CACHED DATABASE SETUP (THE FIX)
# ==========================================
# 👇 This decorator stops it from running every time!
@st.cache_resource 
def initialize_system():
    """Forces table creation and Admin user generation on startup."""
    print("⚡ INITIALIZING DATABASE SYSTEM (Running Once)...")
    try:
        # 1. Force Create All Tables
        Base.metadata.create_all(bind=engine)
        
        # 2. Create Admin User
        db = SessionLocal()
        admin_email = os.getenv("SENDER_EMAIL") 
        
        # Only query if admin_email is set
        if admin_email:
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

# Call the cached function
initialize_system()

# ==========================================
# 4. CUSTOM STYLES
# ==========================================
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
#      LOGIN SCREEN (ZERO-FADE VERSION)
# ==========================================
if st.session_state.user_email is None:
    
    # Create a container that we can completely replace
    login_container = st.container()
    
    with login_container:
        st.title("🏢 VOLTA HR Portal")
        st.info("Log in with your credentials.")
        
        with st.form("login_form", clear_on_submit=True):
            email_input = st.text_input("Email", key="login_email")
            password_input = st.text_input("Password", type="password", key="login_pass")
            
            submitted = st.form_submit_button("Login", type="primary")
            
            if submitted:
                email = email_input.strip().lower()
                password = password_input
                
                if email and password:
                    try:
                        login_db = SessionLocal()
                        user = login_db.query(Employee).filter(
                            Employee.email == email, 
                            Employee.password == password
                        ).first()
                        login_db.close()
                        
                        if user:
                            # Clear the container FIRST
                            login_container.empty()
                            
                            # Then set session state
                            st.session_state.user_email = user.email
                            st.session_state.role = user.role
                            st.session_state.notification_checked = False #Reset notification check on login
                            
                            # Force immediate rerun
                            st.rerun()
                            # st.stop() # we are making the login form to stop render in the chat session
                            

                        else:
                            st.error("❌ Invalid Credentials. Please try again.")
                    except Exception as e:
                        st.error(f"❌ Connection Error: {e}")
                else:
                    st.warning("⚠️ Please enter both email and password.")
    
    # Stop execution here to prevent any bleeding into main interface
    st.stop()

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
        if user_obj and user_obj.onboarding_status == "active" and st.session_state.get("last_status") != "active":
             st.session_state["last_status"] = "active"
             st.rerun() 

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
        @st.fragment(run_every=2) # checks 2 seconds for updates
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
                            msg = f"👋 **Welcome Admin!**\n\nUpdates: {p_leave} Leave, {p_onboard} Onboarding pending.\n\nType **'show pending requests'**."
                        else:
                            msg = "👋 **Welcome Admin!** whatsup"

                        current_session["messages"].append({"role": "assistant", "content": msg})
                       
                        # time.sleep(1)
                        st.rerun()

                    elif current_total > last_total:
                        st.session_state.last_notif_check["admin_pending_count"] = current_total 
                        new_count = current_total - last_total
                        st.toast(f"🔔 {new_count} New Request(s)!", icon="🔔")
                        current_session["messages"].append({"role": "assistant", "content": f"🔔 **New Request Received!**\nTotal Pending: {current_total}\nType **'show pending requests'**."})
                       
                        # time.sleep(2)
                        st.rerun()
                    
                    # if current_total != last_total:
                    #     st.session_state.last_notif_check["admin_pending_count"] = current_total

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
                        
                        # time.sleep(1)
                        st.rerun()

                    elif last_leave and last_leave.status in ["approved", "rejected"]:
                        last_leave.notification_seen = True
                        local_db.commit()
                        icon = "✅" if last_leave.status == "approved" else "❌"
                        msg = f"{icon} **Update:** Your leave for **{last_leave.start_date.date()}** was **{last_leave.status.upper()}**."
                        st.toast(f"Leave {last_leave.status.title()}!", icon=icon)
                        current_session["messages"].append({"role": "assistant", "content": msg})
                        
                        # time.sleep(2)
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

            

            # 🔥 auto-refresh every 2 seconds until approved
            # st.experimental_set_query_params(_=time.time())
            # time.sleep(2)
            # st.rerun()

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
                    
                    assistant_placeholder = st.empty()
                    streamed_text = ""
                    final_state = None   # <-- IMPORTANT

                    for chunk in graph.stream(state):
                        if "messages" in chunk:
                            final_state = chunk              # keep last valid state
                            last = chunk["messages"][-1]
                            if last["role"] == "assistant":
                                streamed_text = last["content"]
                                assistant_placeholder.markdown(streamed_text)

                    # SAFETY FALLBACK
                    if final_state is None:
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
                
                # st.rerun()

        
    finally:
        # ALWAYS CLOSE THE DB SESSION TO PREVENT LEAKS
        db.close()