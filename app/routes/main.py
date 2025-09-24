"""
Main routes for the Chat Application.
Handles home page and general navigation.
"""
from flask import Blueprint, render_template, session

# Create blueprint for main routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page route."""
    return render_template('index.html')