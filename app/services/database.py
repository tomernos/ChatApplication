"""
Database service layer for Chat Application.
Handles all database operations with proper error handling and logging.
"""
import logging
from app.models import User, ChatMessage, SessionLocal, get_db_session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

# Simple logger
logger = logging.getLogger(__name__)

class DatabaseService:
    """Service class for database operations."""
    
    @staticmethod
    def create_user(user_id: str, username: str, password: str, 
                   classification: str = 'A', age: int = None, email: str = None) -> bool:
        """Create a new user in the database."""
        db = get_db_session()
        try:
            new_user = User(
                id=user_id,
                username=username,
                password=password,
                classification=classification,
                age=age,
                email=email
            )
            db.add(new_user)
            db.commit()
            logger.info(f"User {username} created successfully")
            return True
        except IntegrityError as e:
            db.rollback()
            logger.error(f"IntegrityError creating user {username}: {e}")
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error creating user {username}: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def verify_user(username: str, password: str) -> Optional[User]:
        """
        Verify user credentials.
        Returns User object if valid, None otherwise.
        """
        db = get_db_session()
        try:
            user = db.query(User).filter(
                User.username == username, 
                User.password == password
            ).first()
            return user  # Returns User object or None
        except Exception as e:
            logger.error(f"Error verifying user: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """Get user by username."""
        db = get_db_session()
        try:
            user = db.query(User).filter(User.username == username).first()
            return user
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by ID."""
        db = get_db_session()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            return user
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_all_users() -> List[User]:
        """Get all users from the database."""
        db = get_db_session()
        try:
            users = db.query(User).all()
            return users
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def update_user(user_id: str, **kwargs) -> bool:
        """Update user information."""
        db = get_db_session()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            for key, value in kwargs.items():
                if hasattr(user, key) and value is not None:
                    setattr(user, key, value)
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error updating user: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def delete_user(user_id: str) -> bool:
        """Delete user from database."""
        db = get_db_session()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                db.delete(user)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            print(f"Error deleting user: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def count_users() -> int:
        """Count total number of users."""
        db = get_db_session()
        try:
            count = db.query(User).count()
            return count
        except Exception as e:
            print(f"Error counting users: {e}")
            return 0
        finally:
            db.close()
    
    @staticmethod
    def create_chat_message(username: str, message: str) -> bool:
        """Create a new chat message."""
        db = get_db_session()
        try:
            new_message = ChatMessage(username=username, message=message)
            db.add(new_message)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error creating message: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def get_all_messages() -> List[ChatMessage]:
        """Get all chat messages ordered by timestamp."""
        db = get_db_session()
        try:
            messages = db.query(ChatMessage).order_by(ChatMessage.timestamp.asc()).all()
            return messages
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_message_by_id(message_id: int) -> Optional[ChatMessage]:
        """
        Get a specific message by ID.
        Used for message deletion verification.
        """
        db = get_db_session()
        try:
            message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
            return message
        except Exception as e:
            print(f"Error getting message by ID: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def delete_message(message_id: int) -> bool:
        """
        Delete a specific message by ID.
        Returns True if deleted successfully, False otherwise.
        """
        db = get_db_session()
        try:
            message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
            if message:
                db.delete(message)
                db.commit()
                print(f"Message {message_id} deleted successfully!")
                return True
            else:
                print(f"Message {message_id} not found")
                return False
        except Exception as e:
            db.rollback()
            print(f"Error deleting message: {e}")
            return False
        finally:
            db.close()

# Create database service instance
db_service = DatabaseService()