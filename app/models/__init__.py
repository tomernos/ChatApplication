"""
Database models for the Chat Application.
Defines the structure of database tables using SQLAlchemy.
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from datetime import datetime
from config import Config

# Create the base class for declarative models
Base = declarative_base()

class User(Base):
    """User model for storing user information."""
    __tablename__ = "users"

    key = Column(Integer, primary_key=True, index=True)
    id = Column(String(9), unique=True, nullable=False)
    username = Column(String(55), unique=True, nullable=False)
    password = Column(String, nullable=False)
    classification = Column(String(1))
    age = Column(Integer)
    email = Column(String(55))

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class ChatMessage(Base):
    """Chat message model for storing chat messages."""
    __tablename__ = "chat_messages"

    key = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ChatMessage(username='{self.username}', timestamp='{self.timestamp}')>"

# Database engine and session setup
def create_database_engine(database_url=None):
    """Create and return database engine."""
    if not database_url:
        database_url = Config.DATABASE_URL
    
    print(f"Using database: {database_url}")
    engine = create_engine(database_url)
    
    # Create database if it doesn't exist (for PostgreSQL)
    if not database_exists(engine.url):
        create_database(engine.url)
        print("Database created successfully!")
    
    return engine

# Create engine and session factory
engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def get_db_session():
    """Get a database session."""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e