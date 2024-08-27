import sqlite3 as sql3
import hashlib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'example.db')

def create_table():
    conn = sql3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        key INTEGER PRIMARY KEY,
        id INT,
        username VARCHAR(55),
        password TEXT,
        classification CHAR(1),
        age INT,
        email VARCHAR(55)
    )
    ''')
    
    conn.commit()
    conn.close()

def create_chat_table():
    conn = sql3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_messages (
        key INTEGER PRIMARY KEY,
        username TEXT,
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def verify_user(username, password):
    conn = sql3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        stored_password = row[0]
        encrypted_password = hashlib.sha256(password.encode()).hexdigest()
        if stored_password == encrypted_password:
            return True
    return False

def insert_user(id, username, password, classification, age, email):
    conn = sql3.connect(db_path)
    cursor = conn.cursor()
    
    # Encrypt the password
    encrypted_password = hashlib.sha256(password.encode()).hexdigest()
    
    cursor.execute('''
    INSERT INTO users (id, username, password, classification, age, email) VALUES (?, ?, ?, ?, ?, ?)
    ''', (id, username, encrypted_password, classification, age, email))
    
    conn.commit()
    conn.close()

def review_users():
    conn = sql3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    
    conn.close()
    return rows

def delete_user(user_id):
    conn = sql3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    
    conn.commit()
    conn.close()

def modify_user(user_id, username=None, password=None, classification=None, age=None, email=None):
    conn = sql3.connect(db_path)
    cursor = conn.cursor()
    
    if username:
        cursor.execute('UPDATE users SET username = ? WHERE id = ?', (username, user_id))
    if password:
        encrypted_password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute('UPDATE users SET password = ? WHERE id = ?', (encrypted_password, user_id))
    if classification:
        cursor.execute('UPDATE users SET classification = ? WHERE id = ?', (classification, user_id))
    if age:
        cursor.execute('UPDATE users SET age = ? WHERE id = ?', (age, user_id))
    if email:
        cursor.execute('UPDATE users SET email = ? WHERE id = ?', (email, user_id))
    
    conn.commit()
    conn.close()

def count_users():
    conn = sql3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users')
    count = cursor.fetchone()[0]
    
    conn.close()
    return count

def find_user_by_id(user_id):
    conn = sql3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    return user
##########################################
#          CHAT FUNCTIONS                #
##########################################

def insert_chat_message(username, message):
    conn = sql3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO chat_messages (username, message) VALUES (?, ?)
    ''', (username, message))
    
    conn.commit()
    conn.close()

def get_all_chat_messages():
    conn = sql3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT username, message, timestamp FROM chat_messages ORDER BY timestamp ASC')
    messages = cursor.fetchall()
    
    conn.close()
    return messages