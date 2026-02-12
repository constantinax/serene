import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use DATABASE_URL environment variable or default to a local SQLite file for development
DATABASE_URL = os.getenv("project2.syros.aegean.gr", "sqlite:///./test.db")

# For SQLite we need to pass check_same_thread
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
