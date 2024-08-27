import os
import pymysql
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    DB_NAME = os.environ.get('DB_NAME', 'flaskdata')
    DB_USER = os.environ.get('DB_USER', 'tomer')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '12341234')
    DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')

    # Create database if it doesn't exist
    pymysql.install_as_MySQLdb()
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    conn.close()

    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy
    db.init_app(app)

    # Create tables
    with app.app_context():
        import models  # Import here to avoid circular imports
        db.create_all()