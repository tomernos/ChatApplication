import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from my_flask import app
from database import SessionLocal, User, ChatMessage

class TestMyFlask(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_index_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Flask App', response.data)


if __name__ == '__main__':
    unittest.main()