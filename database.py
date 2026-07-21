from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os


load_dotenv()


# SQLite database location
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./health_ai.db"
)


# SQLite needs this option for FastAPI
connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)


# Create database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class for SQLAlchemy models
Base = declarative_base()



# Dependency for API routes
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()