import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()
# Get database connection details from environment variables
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_PORT = os.environ.get('DB_PORT')

# Create the database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()

# Define your models
class User(Base):
    __tablename__ = "users"

    key = Column(Integer, primary_key=True, index=True)
    id = Column(Integer)
    username = Column(String(55))
    password = Column(String)
    classification = Column(String(1))
    age = Column(Integer)
    email = Column(String(55))

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    key = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Database operations
def create_table():
    Base.metadata.create_all(bind=engine)

def create_chat_table():
    Base.metadata.create_all(bind=engine)

def insert_user(id, username, password, classification, age, email):
    db = SessionLocal()
    new_user = User(id=id, username=username, password=password, classification=classification, age=age, email=email)
    db.add(new_user)
    db.commit()
    db.close()

def review_users():
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return users

def delete_user(user_id):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    db.close()

def modify_user(user_id, username=None, password=None, classification=None, age=None, email=None):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        if username:
            user.username = username
        if password:
            user.password = password
        if classification:
            user.classification = classification
        if age:
            user.age = age
        if email:
            user.email = email
        db.commit()
    db.close()

def count_users():
    db = SessionLocal()
    count = db.query(User).count()
    db.close()
    return count

def find_user_by_id(user_id):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    return user

def verify_user(username, password):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username, User.password == password).first()
    db.close()
    return user is not None

def insert_chat_message(username, message):
    db = SessionLocal()
    new_message = ChatMessage(username=username, message=message)
    db.add(new_message)
    db.commit()
    db.close()

def get_all_chat_messages():
    db = SessionLocal()
    messages = db.query(ChatMessage).order_by(ChatMessage.timestamp.asc()).all()
    db.close()
    return messages