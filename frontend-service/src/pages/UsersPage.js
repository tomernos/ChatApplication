/**
 * Users List Page Component
 * 
 * Displays all registered users.
 * Replaces user_list.html template.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { userAPI } from '../services/api';
import '../styles/UsersPage.css';

function UsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const data = await userAPI.getAllUsers();
      setUsers(data.users || []);
    } catch (err) {
      setError('Failed to load users');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div>
      <nav className="navbar">
        <div className="navbar-brand">ConnectHub</div>
        <div className="navbar-menu">
          <a href="#" onClick={() => navigate('/chat')}>Chat</a>
          <a href="#" onClick={() => navigate('/profile')}>Profile</a>
          <a href="#" onClick={() => navigate('/login')}>Logout</a>
        </div>
      </nav>

      <div className="glass-container" style={{ maxWidth: '800px' }}>
        <h1>Community Members</h1>
        <p style={{ textAlign: 'center', color: '#666', marginBottom: '2rem' }}>
          {users.length} {users.length === 1 ? 'member' : 'members'} in ConnectHub
        </p>

        {error && <div className="alert alert-error">{error}</div>}

        <div className="users-grid">
          {users.map((user) => (
            <div key={user.id} className="user-card">
              <div className="user-avatar">
                {user.username.charAt(0).toUpperCase()}
              </div>
              <h3>{user.username}</h3>
              <p className="user-email">{user.email}</p>
              <p className="user-joined">
                Joined {new Date(user.created_at).toLocaleDateString()}
              </p>
            </div>
          ))}
        </div>

        <button 
          className="btn btn-primary"
          onClick={() => navigate('/chat')}
        >
          Back to Chat
        </button>
      </div>
    </div>
  );
}

export default UsersPage;
