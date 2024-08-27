import mysql.connector
import hashlib
import os
from mysql.connector import Error

# Connection parameters
db_config = {
    'host': 'localhost',  # or your MySQL server address
    'user': 'your_username',
    'password': 'your_password',
    'database': 'your_database_name'
}

def get_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_table():
    conn = get_connection()
    if conn is not None:
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            `key` INT AUTO_INCREMENT PRIMARY KEY,
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
    conn = get_connection()
    if conn is not None:
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            `key` INT AUTO_INCREMENT PRIMARY KEY,
            username TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()

def verify_user(username, password):
    conn = get_connection()
    if conn is not None:
        cursor = conn.cursor()
        
        cursor.execute('SELECT password FROM users WHERE username = %s', (username,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            stored_password = row[0]
            encrypted_password = hashlib.sha256(password.encode()).hexdigest()
            if stored_password == encrypted_password:
                return True
    return False
def insert_user(id, username, password, classification, age, email):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Encrypt the password
    encrypted_password = hashlib.sha256(password.encode()).hexdigest()
    
    cursor.execute('''
    INSERT INTO users (id, username, password, classification, age, email) VALUES (?, ?, ?, ?, ?, ?)
    ''', (id, username, encrypted_password, classification, age, email))
    
    conn.commit()
    conn.close()

def review_users():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    
    conn.close()
    return rows

def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    
    conn.commit()
    conn.close()

def modify_user(user_id, username=None, password=None, classification=None, age=None, email=None):
    conn = get_connection()
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
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users')
    count = cursor.fetchone()[0]
    
    conn.close()
    return count

def find_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    return user
    
##########################################
#          CHAT FUNCTIONS                #
##########################################

def insert_chat_message(username, message):
    conn = get_connection()
    if conn is not None:
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO chat_messages (username, message) VALUES (%s, %s)
        ''', (username, message))
        
        conn.commit()
        conn.close()

def get_all_chat_messages():
    conn = get_connection()
    if conn is not None:
        cursor = conn.cursor()
        
        cursor.execute('SELECT username, message, timestamp FROM chat_messages ORDER BY timestamp ASC')
        messages = cursor.fetchall()
        
        conn.close()
        return messages
    return []