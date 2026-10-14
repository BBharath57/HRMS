from app.database.db import get_db
from app.database.models import Employee

# 1. Setup DB Connection
db = next(get_db())

# 2. Admin Details
admin_email = "bharathkumarking143@gmail.com"
admin_password = "admin"  # You can change this

# 3. Check if exists
existing = db.query(Employee).filter(Employee.email == admin_email).first()

if existing:
    print(f"❌ User {admin_email} already exists!")
else:
    # 4. Create the Admin User
    admin = Employee(
        name="Admin",
        email=admin_email,
        password=admin_password,
        role="admin",  # <--- THIS IS THE KEY
        onboarding_status="active",
        used_paid_leaves=0,
        used_emergency_leaves=0
    )
    db.add(admin)
    db.commit()
    print(f"✅ Success! Admin created.\nLogin: {admin_email}\nPassword: {admin_password}")