from db_setup import db
from models import User, ChatMessage
import hashlib

def create_tables():
    db.create_all()

def verify_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user:
        encrypted_password = hashlib.sha256(password.encode()).hexdigest()
        return user.password == encrypted_password
    return False

def insert_user(id, username, password, classification, age, email):
    encrypted_password = hashlib.sha256(password.encode()).hexdigest()
    new_user = User(id=id, username=username, password=encrypted_password, 
                    classification=classification, age=age, email=email)
    db.session.add(new_user)
    db.session.commit()

def review_users():
    return User.query.all()

def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        db.session.delete(user)
        db.session.commit()

def modify_user(user_id, username=None, password=None, classification=None, age=None, email=None):
    user = User.query.filter_by(id=user_id).first()
    if user:
        if username:
            user.username = username
        if password:
            user.password = hashlib.sha256(password.encode()).hexdigest()
        if classification:
            user.classification = classification
        if age:
            user.age = age
        if email:
            user.email = email
        db.session.commit()

def count_users():
    return User.query.count()

def find_user_by_id(user_id):
    return User.query.filter_by(id=user_id).first()

def insert_chat_message(username, message):
    new_message = ChatMessage(username=username, message=message)
    db.session.add(new_message)
    db.session.commit()

def get_all_chat_messages():
    return ChatMessage.query.order_by(ChatMessage.timestamp.asc()).all()