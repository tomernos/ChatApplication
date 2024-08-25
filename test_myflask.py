import unittest
from my_flask import app, create_table, create_chat_table
import os

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        
        # Use an in-memory database for testing
        app.config['DATABASE'] = ':memory:'
        with app.app_context():
            create_table()
            create_chat_table()

    def test_index(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Flask App', response.data)

    def test_login(self):
        response = self.app.post('/login', data=dict(
            username='testuser',
            password='testpass'
        ), follow_redirects=True)
        self.assertIn(b'Invalid username or password', response.data)

    def test_insert_user(self):
        response = self.app.post('/insert', data=dict(
            id='1',
            username='newuser',
            password='newpass',
            classification='A',
            age='25',
            email='new@example.com'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()