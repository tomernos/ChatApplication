"""
Redis service layer for Chat Application.
Handles session management, caching, and real-time features.
"""
import redis
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import Config

class RedisService:
    """Service class for Redis operations."""
    
    def __init__(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=Config.REDIS_DB,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            print("Redis connection established successfully!")
        except redis.ConnectionError:
            print("Warning: Redis not available. Session features disabled.")
            self.redis_client = None
        except Exception as e:
            print(f"Redis connection error: {e}")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Check if Redis is available."""
        return self.redis_client is not None
    
    # Session Management
    def store_session(self, session_id: str, user_data: Dict) -> bool:
        """Store user session in Redis."""
        if not self.is_available():
            return False
        
        try:
            self.redis_client.setex(
                f"session:{session_id}",
                3600,  # 1 hour expiry
                json.dumps(user_data)
            )
            print(f"Session stored for session ID: {session_id}")
            return True
        except Exception as e:
            print(f"Error storing session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get user session from Redis."""
        if not self.is_available():
            return None
        
        try:
            data = self.redis_client.get(f"session:{session_id}")
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Error getting session: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete user session from Redis."""
        if not self.is_available():
            return False
        
        try:
            self.redis_client.delete(f"session:{session_id}")
            return True
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    # Online Users Management
    def add_online_user(self, username: str) -> bool:
        """Mark user as online."""
        if not self.is_available():
            return False
        
        try:
            self.redis_client.sadd("online_users", username)
            # Set user-specific online status with expiry
            self.redis_client.setex(f"user_online:{username}", 300, "true")  # 5 minutes
            return True
        except Exception as e:
            print(f"Error adding online user: {e}")
            return False
    
    def remove_online_user(self, username: str) -> bool:
        """Mark user as offline."""
        if not self.is_available():
            return False
        
        try:
            self.redis_client.srem("online_users", username)
            self.redis_client.delete(f"user_online:{username}")
            return True
        except Exception as e:
            print(f"Error removing online user: {e}")
            return False
    
    def get_online_users(self) -> List[str]:
        """Get list of all online users."""
        if not self.is_available():
            return []
        
        try:
            online_users = list(self.redis_client.smembers("online_users"))
            # Clean up expired users
            active_users = []
            for user in online_users:
                if self.redis_client.exists(f"user_online:{user}"):
                    active_users.append(user)
                else:
                    self.redis_client.srem("online_users", user)
            return active_users
        except Exception as e:
            print(f"Error getting online users: {e}")
            return []
    
    def is_user_online(self, username: str) -> bool:
        """Check if a specific user is online."""
        if not self.is_available():
            return False
        
        try:
            return self.redis_client.exists(f"user_online:{username}") == 1
        except Exception as e:
            print(f"Error checking user online status: {e}")
            return False
    
    # Typing Indicators
    def set_typing_indicator(self, username: str, room_id: str = "general") -> bool:
        """Set typing indicator for a user in a room."""
        if not self.is_available():
            return False
        
        try:
            self.redis_client.setex(f"typing:{room_id}:{username}", 5, "true")  # 5 seconds
            return True
        except Exception as e:
            print(f"Error setting typing indicator: {e}")
            return False
    
    def get_typing_users(self, room_id: str = "general") -> List[str]:
        """Get users currently typing in a room."""
        if not self.is_available():
            return []
        
        try:
            pattern = f"typing:{room_id}:*"
            typing_keys = self.redis_client.keys(pattern)
            typing_users = [key.split(':')[-1] for key in typing_keys]
            return typing_users
        except Exception as e:
            print(f"Error getting typing users: {e}")
            return []
    
    # Caching
    def cache_user_data(self, username: str, user_data: Dict, expiry: int = 300) -> bool:
        """Cache user data for faster access."""
        if not self.is_available():
            return False
        
        try:
            self.redis_client.setex(
                f"user_cache:{username}",
                expiry,
                json.dumps(user_data)
            )
            return True
        except Exception as e:
            print(f"Error caching user data: {e}")
            return False
    
    def get_cached_user_data(self, username: str) -> Optional[Dict]:
        """Get cached user data."""
        if not self.is_available():
            return None
        
        try:
            data = self.redis_client.get(f"user_cache:{username}")
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Error getting cached user data: {e}")
            return None
    
    # Statistics
    def increment_message_count(self, username: str) -> int:
        """Increment and return user's message count."""
        if not self.is_available():
            return 0
        
        try:
            return self.redis_client.incr(f"message_count:{username}")
        except Exception as e:
            print(f"Error incrementing message count: {e}")
            return 0
    
    def get_message_count(self, username: str) -> int:
        """Get user's message count."""
        if not self.is_available():
            return 0
        
        try:
            count = self.redis_client.get(f"message_count:{username}")
            return int(count) if count else 0
        except Exception as e:
            print(f"Error getting message count: {e}")
            return 0

# Create Redis service instance
redis_service = RedisService()