

# """
# SQLAlchemy models for HRMS.
# """
# """
# models.py
# """
# from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
# from sqlalchemy.orm import relationship, declarative_base
# from datetime import datetime

# Base = declarative_base()

# class Employee(Base):
#     __tablename__ = "employees"
    
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=True)
#     email = Column(String, unique=True, index=True)
    
#     # --- NEW FIELDS ---
#     personal_email = Column(String, nullable=True)
#     role = Column(String, default="employee") # Developer / Non-Tech
#     dob = Column(String, nullable=True)
#     nationality = Column(String, nullable=True)
#     age = Column(Integer, nullable=True)
#     leaves_balance = Column(Integer, default=24) # Default allocated leaves
#     # ------------------
    
#     onboarding_status = Column(String, default="pending") # pending, pending_approval, completed
#     created_at = Column(DateTime, default=datetime.utcnow)

#     # Relationships
#     onboarding = relationship("Onboarding", back_populates="employee", uselist=False)
#     leave_requests = relationship("LeaveRequest", back_populates="employee")

# class Onboarding(Base):
#     __tablename__ = "onboarding"
    
#     id = Column(Integer, primary_key=True, index=True)
#     employee_id = Column(Integer, ForeignKey("employees.id"))
#     step = Column(Integer, default=1)
#     data = Column(Text, default="")
#     completed = Column(Boolean, default=False)
    
#     employee = relationship("Employee", back_populates="onboarding")

# class LeaveRequest(Base):
#     __tablename__ = "leave_requests"
    
#     id = Column(Integer, primary_key=True, index=True)
#     employee_id = Column(Integer, ForeignKey("employees.id"))
#     reason = Column(String)
#     start_date = Column(DateTime)
#     end_date = Column(DateTime)
#     type = Column(String) # Paid, Emergency, etc.
#     status = Column(String, default="pending")
#     approved_by = Column(Integer, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
    
#     employee = relationship("Employee", back_populates="leave_requests")


"""
models.py
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="New User")
    email = Column(String, unique=True, index=True)
    password = Column(String)  # NEW: For Login
    role = Column(String, default="employee") # 'admin' or 'employee'
    
    # NEW STATUS FLOW: 
    # 'signed_up' -> 'onboarding_triggered' -> 'details_submitted' -> 'active'
    onboarding_status = Column(String, default="signed_up") 
    
    # NEW LEAVE QUOTAS
    used_paid_leaves = Column(Integer, default=0)      # Limit: 1
    used_emergency_leaves = Column(Integer, default=0) # Limit: 1
    
    personal_email = Column(String, nullable=True)
    employee_id_str = Column(String, nullable=True) # Generated after onboarding
    
    # Demographics
    age = Column(Integer, nullable=True)
    dob = Column(String, nullable=True)
    nationality = Column(String, nullable=True)
    address = Column(String, nullable=True)

class Onboarding(Base):
    __tablename__ = "onboarding"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    step = Column(Integer, default=1)
    data = Column(String, default="")
    completed = Column(Boolean, default=False)

class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    reason = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    type = Column(String) # 'paid', 'unpaid', 'emergency'
    status = Column(String, default="pending_approval")
    approved_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    notification_seen = Column(Boolean, default=False)  # NEW: Track if user saw the status update