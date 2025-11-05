/**
 * Chat Page Component
 * 
 * Main chat interface where users send and view messages.
 * Replaces the old chat.html template.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { chatAPI, authAPI } from '../services/api';
import '../styles/ChatPage.css';

function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();

  // Load messages and user info when component mounts
  useEffect(() => {
    loadInitialData();
    
    // Auto-refresh messages every 3 seconds
    const interval = setInterval(loadMessages, 3000);
    
    // Cleanup: stop interval when component unmounts
    return () => clearInterval(interval);
  }, []);

  const loadInitialData = async () => {
    try {
      // Load current user
      const userData = await authAPI.getCurrentUser();
      setCurrentUser(userData.user);
      
      // Load messages
      await loadMessages();
    } catch (err) {
      console.error('Failed to load data:', err);
      // If unauthorized, redirect to login
      if (err.response?.status === 401) {
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const loadMessages = async () => {
    try {
      const data = await chatAPI.getMessages();
      setMessages(data.messages || []);
    } catch (err) {
      console.error('Failed to load messages:', err);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim()) {
      return; // Don't send empty messages
    }

    try {
      await chatAPI.sendMessage(newMessage);
      setNewMessage(''); // Clear input
      await loadMessages(); // Reload messages
    } catch (err) {
      setError('Failed to send message. Please try again.');
    }
  };

  const handleDeleteMessage = async (messageId) => {
    if (!window.confirm('Are you sure you want to delete this message?')) {
      return;
    }

    try {
      await chatAPI.deleteMessage(messageId);
      await loadMessages(); // Reload messages
    } catch (err) {
      setError('Failed to delete message.');
    }
  };

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      navigate('/login');
    } catch (err) {
      console.error('Logout failed:', err);
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
    <div className="chat-page">
      {/* Navigation bar */}
      <nav className="navbar">
        <div className="navbar-brand">ConnectHub</div>
        <div className="navbar-menu">
          <span>Welcome, {currentUser?.username}!</span>
          <a href="#" onClick={() => navigate('/profile')}>Profile</a>
          <a href="#" onClick={() => navigate('/users')}>Users</a>
          <a href="#" onClick={handleLogout}>Logout</a>
        </div>
      </nav>

      {/* Chat container */}
      <div className="chat-container">
        <h2>Chat Room</h2>

        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        {/* Messages list */}
        <div className="messages-list">
          {messages.length === 0 ? (
            <p className="no-messages">No messages yet. Start the conversation!</p>
          ) : (
            messages.map((message) => (
              <div 
                key={message.id} 
                className={`message ${message.user_id === currentUser?.id ? 'own-message' : ''}`}
              >
                <div className="message-header">
                  <strong>{message.username || 'Anonymous'}</strong>
                  <span className="message-time">
                    {new Date(message.created_at).toLocaleString()}
                  </span>
                </div>
                <div className="message-content">{message.content}</div>
                {message.user_id === currentUser?.id && (
                  <button
                    className="btn-delete-message"
                    onClick={() => handleDeleteMessage(message.id)}
                  >
                    Delete
                  </button>
                )}
              </div>
            ))
          )}
        </div>

        {/* Message input form */}
        <form onSubmit={handleSendMessage} className="message-form">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type your message..."
            className="message-input"
          />
          <button type="submit" className="btn btn-primary">
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

export default ChatPage;
