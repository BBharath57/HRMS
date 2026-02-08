"""
add_notification_seen_column.py

Migration script to add notification_seen column to leave_requests table.
Run this ONCE after updating models.py
"""
from sqlalchemy import text
from db import engine

def migrate():
    """Add notification_seen column to existing database"""
    try:
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='leave_requests' 
                AND column_name='notification_seen'
            """))
            
            if result.fetchone():
                print("✅ Column 'notification_seen' already exists. No migration needed.")
                return
            
            # Add the column
            print("🔧 Adding 'notification_seen' column to leave_requests table...")
            conn.execute(text("""
                ALTER TABLE leave_requests 
                ADD COLUMN notification_seen BOOLEAN DEFAULT FALSE
            """))
            conn.commit()
            
            print("✅ Migration completed successfully!")
            print("📝 All existing leave requests will have notification_seen=False by default.")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("\nIf you see 'column already exists' error, you can ignore this.")

if __name__ == "__main__":
    migrate()
