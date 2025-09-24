"""
Queue service layer for Chat Application.
Handles background tasks and message queuing with RabbitMQ.
"""
import pika
import json
from datetime import datetime
from typing import Dict, Callable
from config import Config
import threading

class QueueService:
    """Service class for RabbitMQ operations."""
    
    def __init__(self):
        """Initialize RabbitMQ connection."""
        try:
            self.connection_params = pika.ConnectionParameters(
                host=Config.RABBITMQ_HOST,
                port=Config.RABBITMQ_PORT,
                credentials=pika.PlainCredentials(
                    Config.RABBITMQ_USER,
                    Config.RABBITMQ_PASSWORD
                )
            )
            
            # Test connection
            connection = pika.BlockingConnection(self.connection_params)
            connection.close()
            print("RabbitMQ connection established successfully!")
            self.available = True
            
        except Exception as e:
            print(f"Warning: RabbitMQ not available. Queue features disabled. Error: {e}")
            self.available = False
    
    def is_available(self) -> bool:
        """Check if RabbitMQ is available."""
        return self.available
    
    def _get_connection(self):
        """Get a new RabbitMQ connection."""
        if not self.is_available():
            return None
        try:
            return pika.BlockingConnection(self.connection_params)
        except Exception as e:
            print(f"Error creating RabbitMQ connection: {e}")
            return None
    
    def _declare_queues(self, channel):
        """Declare all necessary queues."""
        queues = [
            'email_notifications',
            'push_notifications',
            'message_processing',
            'user_activity',
            'system_logs'
        ]
        
        for queue in queues:
            channel.queue_declare(queue=queue, durable=True)
    
    # Email Notifications
    def queue_email_notification(self, recipient_email: str, subject: str, message: str) -> bool:
        """Queue an email notification."""
        if not self.is_available():
            print("Email queuing skipped: RabbitMQ not available")
            return False
        
        connection = self._get_connection()
        if not connection:
            return False
        
        try:
            channel = connection.channel()
            self._declare_queues(channel)
            
            notification_data = {
                'type': 'email',
                'recipient': recipient_email,
                'subject': subject,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'priority': 'normal'
            }
            
            channel.basic_publish(
                exchange='',
                routing_key='email_notifications',
                body=json.dumps(notification_data),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                )
            )
            
            print(f"Email notification queued for {recipient_email}")
            return True
            
        except Exception as e:
            print(f"Error queuing email notification: {e}")
            return False
        finally:
            if connection and not connection.is_closed:
                connection.close()
    
    # Push Notifications
    def queue_push_notification(self, username: str, title: str, message: str) -> bool:
        """Queue a push notification."""
        if not self.is_available():
            print("Push notification queuing skipped: RabbitMQ not available")
            return False
        
        connection = self._get_connection()
        if not connection:
            return False
        
        try:
            channel = connection.channel()
            self._declare_queues(channel)
            
            notification_data = {
                'type': 'push',
                'username': username,
                'title': title,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            
            channel.basic_publish(
                exchange='',
                routing_key='push_notifications',
                body=json.dumps(notification_data),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                )
            )
            
            print(f"Push notification queued for {username}")
            return True
            
        except Exception as e:
            print(f"Error queuing push notification: {e}")
            return False
        finally:
            if connection and not connection.is_closed:
                connection.close()
    
    # Message Processing
    def queue_message_processing(self, message_data: Dict) -> bool:
        """Queue message for background processing (spam detection, etc.)."""
        if not self.is_available():
            return False
        
        connection = self._get_connection()
        if not connection:
            return False
        
        try:
            channel = connection.channel()
            self._declare_queues(channel)
            
            processing_data = {
                'type': 'message_processing',
                'message_id': message_data.get('id'),
                'username': message_data.get('username'),
                'message': message_data.get('message'),
                'timestamp': datetime.now().isoformat(),
                'tasks': ['spam_check', 'sentiment_analysis', 'content_filter']
            }
            
            channel.basic_publish(
                exchange='',
                routing_key='message_processing',
                body=json.dumps(processing_data),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                )
            )
            
            print("Message queued for processing")
            return True
            
        except Exception as e:
            print(f"Error queuing message processing: {e}")
            return False
        finally:
            if connection and not connection.is_closed:
                connection.close()
    
    # User Activity Logging
    def log_user_activity(self, username: str, activity: str, details: Dict = None) -> bool:
        """Log user activity for analytics."""
        if not self.is_available():
            return False
        
        connection = self._get_connection()
        if not connection:
            return False
        
        try:
            channel = connection.channel()
            self._declare_queues(channel)
            
            activity_data = {
                'type': 'user_activity',
                'username': username,
                'activity': activity,
                'details': details or {},
                'timestamp': datetime.now().isoformat(),
                'session_id': details.get('session_id') if details else None
            }
            
            channel.basic_publish(
                exchange='',
                routing_key='user_activity',
                body=json.dumps(activity_data),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                )
            )
            
            return True
            
        except Exception as e:
            print(f"Error logging user activity: {e}")
            return False
        finally:
            if connection and not connection.is_closed:
                connection.close()
    
    # Background Workers (Consumer Methods)
    def start_email_worker(self, email_handler: Callable):
        """Start background worker for email notifications."""
        if not self.is_available():
            print("Email worker not started: RabbitMQ not available")
            return
        
        def worker():
            connection = self._get_connection()
            if not connection:
                return
                
            try:
                channel = connection.channel()
                self._declare_queues(channel)
                
                def callback(ch, method, properties, body):
                    try:
                        data = json.loads(body)
                        email_handler(data)
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                    except Exception as e:
                        print(f"Error processing email: {e}")
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                
                channel.basic_qos(prefetch_count=1)
                channel.basic_consume(
                    queue='email_notifications',
                    on_message_callback=callback
                )
                
                print("Email worker started. Waiting for messages...")
                channel.start_consuming()
                
            except Exception as e:
                print(f"Email worker error: {e}")
            finally:
                if connection and not connection.is_closed:
                    connection.close()
        
        # Start worker in background thread
        worker_thread = threading.Thread(target=worker, daemon=True)
        worker_thread.start()
        return worker_thread
    
    def start_activity_logger(self, log_handler: Callable):
        """Start background worker for activity logging."""
        if not self.is_available():
            print("Activity logger not started: RabbitMQ not available")
            return
        
        def worker():
            connection = self._get_connection()
            if not connection:
                return
                
            try:
                channel = connection.channel()
                self._declare_queues(channel)
                
                def callback(ch, method, properties, body):
                    try:
                        data = json.loads(body)
                        log_handler(data)
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                    except Exception as e:
                        print(f"Error processing activity log: {e}")
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                
                channel.basic_qos(prefetch_count=1)
                channel.basic_consume(
                    queue='user_activity',
                    on_message_callback=callback
                )
                
                print("Activity logger started. Waiting for messages...")
                channel.start_consuming()
                
            except Exception as e:
                print(f"Activity logger error: {e}")
            finally:
                if connection and not connection.is_closed:
                    connection.close()
        
        # Start worker in background thread
        worker_thread = threading.Thread(target=worker, daemon=True)
        worker_thread.start()
        return worker_thread

# Example email handler function
def handle_email_notification(data: Dict):
    """Handle email notification (placeholder for actual email sending)."""
    print(f"📧 Sending email to {data['recipient']}")
    print(f"   Subject: {data['subject']}")
    print(f"   Message: {data['message']}")
    # Here you would integrate with actual email service (SendGrid, SES, etc.)

# Example activity log handler
def handle_activity_log(data: Dict):
    """Handle activity logging (placeholder for actual logging system)."""
    print(f"📊 Activity: {data['username']} - {data['activity']}")
    print(f"   Details: {data['details']}")
    print(f"   Time: {data['timestamp']}")
    # Here you would store in analytics database or send to monitoring service

# Create queue service instance
queue_service = QueueService()