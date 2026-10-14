"""
reset_db.py
"""
from app.database.db import engine
# CRITICAL FIX: Import Base from models, so we get the registry that actually contains Employee
from app.database.models import Base, Employee, Onboarding, LeaveRequest 

if __name__ == "__main__":
    print("🗑️  Dropping old tables...")
    # This will drop tables only if they are registered to this Base
    Base.metadata.drop_all(bind=engine)

    print("🔨 Creating new tables (Employees, Onboarding, LeaveRequests)...")
    # This creates the tables based on the models you defined
    Base.metadata.create_all(bind=engine)

    print("✅ Database Reset! You can restart the app now.")