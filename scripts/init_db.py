"""
Initialize the PostgreSQL database and create tables.
"""
from app.database.db import engine, Base
import app.database.models as models

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")
