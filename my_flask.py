#from flask import Flask, render_template, request, redirect, url_for, session, flash
#from SQL import create_table, insert_user, review_users, delete_user, modify_user, count_users, find_user_by_id, verify_user, insert_chat_message, get_all_chat_messages
from flask import *
from SQL import *
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize the database
create_table()
create_chat_table()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if verify_user(username, password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))




@app.route('/insert', methods=['GET', 'POST'])
def insert():
    if request.method == 'POST':
        id = request.form['id']
        username = request.form['username']
        password = request.form['password']
        classification = request.form['classification']
        age = request.form['age']
        email = request.form['email']
        insert_user(id, username, password, classification, age, email)
        return redirect(url_for('index'))
    return render_template('insert.html')

@app.route('/review')
def review():
    users = review_users()
    total_users = count_users()
    return render_template('review.html', users=users, total_users=total_users)

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        user_id = request.form['user_id']
        delete_user(user_id)
        return redirect(url_for('index'))
    return render_template('delete.html')

@app.route('/modify', methods=['GET', 'POST'])
def modify():
    if request.method == 'POST':
        user_id = request.form['user_id']
        username = request.form['username'] or None
        password = request.form['password'] or None
        classification = request.form['classification'] or None
        age = request.form['age'] or None
        email = request.form['email'] or None
        modify_user(user_id, username, password, classification, age, email)
        return redirect(url_for('index'))
    return render_template('modify.html')

@app.route('/count')
def count():
    total_users = count_users()
    return render_template('count.html', total_users=total_users)

@app.route('/find', methods=['GET', 'POST'])
def find():
    if request.method == 'POST':
        user_id = request.form['user_id']
        user = find_user_by_id(user_id)
        return render_template('find.html', user=user)
    return render_template('find.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        message = request.form['message']
        insert_chat_message(session['username'], message)
        return redirect(url_for('chat'))

    messages = get_all_chat_messages()
    return render_template('chat.html', messages=messages)


if __name__ == '__main__':
    print(os.getcwd())
    print(app.template_folder)
    app.run(host='0.0.0.0', port=5000)


