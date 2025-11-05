/**
 * Profile Page Component
 * 
 * Displays and allows editing of user profile.
 * Replaces profile.html template.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';

function ProfilePage() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const data = await authAPI.getCurrentUser();
      setUser(data.user);
    } catch (err) {
      console.error('Failed to load profile:', err);
      navigate('/login');
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
          <a href="#" onClick={() => navigate('/users')}>Users</a>
          <a href="#" onClick={() => navigate('/login')}>Logout</a>
        </div>
      </nav>

      <div className="glass-container">
        <h1>My Profile</h1>
        
        <div style={{ marginTop: '2rem' }}>
          <div className="form-group">
            <label>Username</label>
            <input type="text" value={user?.username || ''} disabled />
          </div>

          <div className="form-group">
            <label>Email</label>
            <input type="email" value={user?.email || ''} disabled />
          </div>

          <div className="form-group">
            <label>Member Since</label>
            <input 
              type="text" 
              value={user?.created_at ? new Date(user.created_at).toLocaleDateString() : ''} 
              disabled 
            />
          </div>

          <button 
            className="btn btn-primary"
            onClick={() => navigate('/chat')}
          >
            Back to Chat
          </button>
        </div>
      </div>
    </div>
  );
}

export default ProfilePage;
