# """
# Database setup for PostgreSQL using SQLAlchemy.
# """
# import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# from dotenv import load_dotenv

# load_dotenv()

# POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
# POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "yourpassword")
# POSTGRES_DB = os.getenv("POSTGRES_DB", "hrms")
# POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
# POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# DATABASE_URL = os.getenv("DATABASE_URL")

# # DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()





import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# =========================================================
#  DATABASE CONNECTION LOGIC
# =========================================================

# 1. Get the Database URL from Environment
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Configure based on what we found
if DATABASE_URL:
    print("✅ Using Cloud/Env Database")
    # Fix for Render's URL format (postgres:// -> postgresql://)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Create Engine for PostgreSQL
    engine = create_engine(DATABASE_URL)

else:
    print("⚠️  No DATABASE_URL found. Using Local SQLite Database.")
    DATABASE_URL = "sqlite:///./hrms.db"
    
    # ⚠️ CRITICAL FOR SQLITE IN STREAMLIT/FASTAPI:
    # "check_same_thread": False is required for SQLite to work in multi-threaded apps
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )

# =========================================================
#  SESSION & BASE
# =========================================================
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
