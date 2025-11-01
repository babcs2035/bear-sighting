import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

load_dotenv()

# Load the database URL from environment variables.
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables.")  # 🚨 Raise an error if DATABASE_URL is missing.

# Create the database engine.
engine = create_engine(DATABASE_URL)

# Configure the session factory.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


def get_db():
    """
    Dependency for getting a database session.
    Ensures the session is properly closed after use.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # 🔒 Close the session to release resources.
