"""
Initialize the PostgreSQL database and create tables.
"""
from db import engine, Base
import models

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")
