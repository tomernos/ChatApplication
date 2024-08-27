from db_setup import db
from datetime import datetime

class User(db.Model):
    key = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.Integer, unique=True, nullable=False)
    username = db.Column(db.String(55), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    classification = db.Column(db.String(1))
    age = db.Column(db.Integer)
    email = db.Column(db.String(55), unique=True, nullable=False)

class ChatMessage(db.Model):
    key = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(55), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)