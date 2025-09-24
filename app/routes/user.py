"""
User management routes for the Chat Application.
Handles user CRUD operations and profile management.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.services.database import db_service
from app.services.redis_service import redis_service

# Create blueprint for user routes
user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
def profile():
    """User profile page."""
    if 'username' not in session:
        flash('Please log in to view profile')
        return redirect(url_for('auth.login'))
    
    username = session['username']
    user = db_service.get_user_by_username(username)
    
    if not user:
        flash('User not found')
        return redirect(url_for('main.index'))
    
    # Get user statistics from Redis if available
    message_count = 0
    if redis_service.is_available():
        message_count = redis_service.get_message_count(username)
    
    return render_template('profile.html', user=user, message_count=message_count)

@user_bp.route('/list')
def user_list():
    """List all users page."""
    if 'username' not in session:
        flash('Please log in to view users')
        return redirect(url_for('auth.login'))
    
    users = db_service.get_all_users()
    return render_template('user_list.html', users=users)

@user_bp.route('/find', methods=['GET', 'POST'])
def find_user():
    """Find user by ID."""
    if 'username' not in session:
        flash('Please log in to find users')
        return redirect(url_for('auth.login'))
    
    user = None
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        if user_id:
            user = db_service.get_user_by_id(user_id)
            if not user:
                flash(f'User with ID {user_id} not found')
        else:
            flash('Please enter a user ID')
    
    return render_template('find_user.html', user=user)

@user_bp.route('/count')
def count_users():
    """Display user count."""
    if 'username' not in session:
        flash('Please log in to view statistics')
        return redirect(url_for('auth.login'))
    
    count = db_service.count_users()
    return render_template('count.html', count=count)

@user_bp.route('/modify/<user_id>', methods=['GET', 'POST'])
def modify_user(user_id):
    """Modify user information."""
    if 'username' not in session:
        flash('Please log in to modify users')
        return redirect(url_for('auth.login'))
    
    # Check if user is modifying their own profile or is admin
    current_user = db_service.get_user_by_username(session['username'])
    target_user = db_service.get_user_by_id(user_id)
    
    if not target_user:
        flash('User not found')
        return redirect(url_for('user.list_users'))
    
    # Allow users to modify their own profile or admins to modify any profile
    if current_user.id != user_id and current_user.classification != 'A':
        flash('You can only modify your own profile')
        return redirect(url_for('user.profile'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        age = request.form.get('age')
        
        updates = {}
        if username and username != target_user.username:
            updates['username'] = username
        if email and email != target_user.email:
            updates['email'] = email
        if age:
            try:
                updates['age'] = int(age)
            except ValueError:
                flash('Age must be a valid number')
                return render_template('modify_user.html', user=target_user)
        
        if updates:
            if db_service.update_user(user_id, **updates):
                flash('User updated successfully')
                
                # Clear cached user data in Redis
                if redis_service.is_available() and username:
                    redis_service.redis_client.delete(f"user_cache:{target_user.username}")
                    if updates.get('username'):
                        redis_service.redis_client.delete(f"user_cache:{username}")
                
                return redirect(url_for('user.profile') if current_user.id == user_id else url_for('user.list_users'))
            else:
                flash('Failed to update user')
        else:
            flash('No changes made')
    
    return render_template('modify_user.html', user=target_user)

@user_bp.route('/delete/<user_id>', methods=['POST'])
def delete_user(user_id):
    """Delete user."""
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    current_user = db_service.get_user_by_username(session['username'])
    
    # Only admins can delete users
    if current_user.classification != 'A':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Cannot delete yourself
    if current_user.id == user_id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    target_user = db_service.get_user_by_id(user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    if db_service.delete_user(user_id):
        # Clean up Redis data
        if redis_service.is_available():
            redis_service.remove_online_user(target_user.username)
            redis_service.redis_client.delete(f"user_cache:{target_user.username}")
            redis_service.redis_client.delete(f"message_count:{target_user.username}")
        
        return jsonify({'success': True, 'message': 'User deleted successfully'})
    else:
        return jsonify({'error': 'Failed to delete user'}), 500

@user_bp.route('/online')
def online_users():
    """Get online users as JSON."""
    if redis_service.is_available():
        users = redis_service.get_online_users()
        return jsonify({'online_users': users})
    else:
        return jsonify({'online_users': [], 'message': 'Redis not available'})