# Frontend-Backend Integration Guide

## 🔄 **How React and Flask Work Together**

### **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                     USER'S BROWSER                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │  React App (localhost:3000)                        │    │
│  │  - Components (LoginPage, ChatPage, etc.)          │    │
│  │  - State Management (useState, useEffect)          │    │
│  │  - API Service (axios)                             │    │
│  └─────────────────────┬──────────────────────────────┘    │
└────────────────────────┼───────────────────────────────────┘
                         │
                         │ HTTP Requests (JSON)
                         │ GET/POST/PUT/DELETE
                         │
┌────────────────────────▼───────────────────────────────────┐
│              Flask Backend (localhost:5000)                 │
│  ┌────────────────────────────────────────────────────┐    │
│  │  API Routes (/api/auth, /api/chat, /api/users)    │    │
│  │  - Receive JSON                                    │    │
│  │  - Process Logic                                   │    │
│  │  - Return JSON                                     │    │
│  └─────────────────────┬──────────────────────────────┘    │
│                        │                                    │
│  ┌─────────────────────▼──────────────────────────────┐    │
│  │  Services Layer                                    │    │
│  │  - Database Service (PostgreSQL queries)          │    │
│  │  - Redis Service (Caching)                        │    │
│  │  - Queue Service (RabbitMQ)                       │    │
│  └─────────────────────┬──────────────────────────────┘    │
└────────────────────────┼───────────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────────┐
│                    Database Layer                           │
│  - PostgreSQL: Persistent data storage                     │
│  - Redis: Session caching, online users                    │
│  - RabbitMQ: Asynchronous task processing                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 **Request-Response Flow Examples**

### **Example 1: User Login**

#### **Step 1: User fills login form in React**

```javascript
// LoginPage.js (React Frontend)
const [formData, setFormData] = useState({
  username: '',
  password: ''
});

const handleSubmit = async (e) => {
  e.preventDefault();  // Prevent page reload
  
  // Call API service
  const response = await authAPI.login(formData.username, formData.password);
  
  // Store token in browser
  localStorage.setItem('token', response.token);
  
  // Navigate to chat page
  navigate('/chat');
};
```

**What happens here:**
- `useState()`: React hook that creates reactive variables
- `formData`: Object holding username and password
- `handleSubmit`: Function triggered when form is submitted
- `authAPI.login()`: Makes HTTP request to Flask backend

---

#### **Step 2: API Service sends HTTP request**

```javascript
// api.js (React Frontend)
export const authAPI = {
  login: async (username, password) => {
    const response = await api.post('/auth/login', {
      username,
      password,
    });
    return response.data;
  },
};
```

**What axios does:**
```
POST http://localhost:5000/api/auth/login
Headers: {
  Content-Type: application/json
}
Body: {
  "username": "john",
  "password": "secret123"
}
```

---

#### **Step 3: Flask receives and processes request**

```python
# auth.py (Flask Backend)
@auth_bp.route('/login', methods=['POST'])
def login():
    # 1. Check if request is JSON
    is_json_request = request.is_json
    
    # 2. Extract credentials from JSON body
    data = request.get_json()
    username = data.get('username')  # "john"
    password = data.get('password')  # "secret123"
    
    # 3. Query database to verify credentials
    user = db_service.verify_user(username, password)
    # SQL executed: SELECT * FROM users WHERE username='john' AND password='secret123'
    
    if user:
        # 4. Create session
        session_id = str(uuid.uuid4())  # Generate unique ID: "a1b2c3d4-..."
        session['username'] = username
        session['user_id'] = user.id
        
        # 5. Store in Redis cache (fast lookup)
        redis_service.store_session(session_id, {
            'username': username,
            'login_time': str(datetime.now())
        })
        
        # 6. Return success response as JSON
        return jsonify({
            'success': True,
            'token': session_id,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200
    else:
        # Invalid credentials
        return jsonify({'error': 'Invalid username or password'}), 401
```

**Key concepts:**
- `request.get_json()`: Extracts JSON from HTTP request body
- `db_service.verify_user()`: Queries PostgreSQL database
- `session[]`: Flask's way to store user info in cookie
- `jsonify()`: Converts Python dict to JSON response
- HTTP status codes: 200 = success, 401 = unauthorized

---

#### **Step 4: React receives response and updates UI**

```javascript
// LoginPage.js (React Frontend)
try {
  const response = await authAPI.login(username, password);
  // response = {success: true, token: "abc123", user: {...}}
  
  localStorage.setItem('token', response.token);
  // Stores token in browser for future requests
  
  navigate('/chat');
  // Changes URL to /chat without page reload
} catch (err) {
  setError(err.response?.data?.error || 'Login failed');
  // Shows error message to user
}
```

---

### **Example 2: Fetching Chat Messages**

#### **Step 1: ChatPage loads and fetches messages**

```javascript
// ChatPage.js (React Frontend)
const [messages, setMessages] = useState([]);

useEffect(() => {
  loadMessages();  // Load when component mounts
  
  // Auto-refresh every 3 seconds
  const interval = setInterval(loadMessages, 3000);
  
  // Cleanup: stop interval when component unmounts
  return () => clearInterval(interval);
}, []);  // Empty array = run once on mount

const loadMessages = async () => {
  try {
    const data = await chatAPI.getMessages();
    setMessages(data.messages);  // Update React state
  } catch (err) {
    console.error('Failed to load messages:', err);
  }
};
```

**What this does:**
- `useEffect()`: React hook that runs code when component loads
- `setInterval()`: JavaScript function that repeats code every N milliseconds
- `setMessages()`: Updates React state, triggers re-render
- Return function: Cleanup code when component is removed

---

#### **Step 2: API Service makes GET request**

```javascript
// api.js (React Frontend)
export const chatAPI = {
  getMessages: async () => {
    const response = await api.get('/chat/messages');
    return response.data;
  },
};
```

**HTTP request:**
```
GET http://localhost:5000/api/chat/messages
Headers: {
  Authorization: Bearer abc123,
  Cookie: session=xyz789
}
```

---

#### **Step 3: Flask queries database and returns messages**

```python
# chat.py (Flask Backend)
@chat_bp.route('/messages', methods=['GET'])
def get_messages():
    # 1. Check authentication
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # 2. Query database
    messages = db_service.get_all_messages()
    # SQL: SELECT * FROM messages ORDER BY timestamp ASC
    
    # 3. Convert to JSON format
    messages_list = []
    for msg in messages:
        messages_list.append({
            'id': msg.id,
            'username': msg.username,
            'content': msg.message,
            'created_at': msg.timestamp.isoformat()
        })
    
    # 4. Return JSON response
    return jsonify({
        'success': True,
        'messages': messages_list
    }), 200
```

**Response:**
```json
{
  "success": true,
  "messages": [
    {
      "id": 1,
      "username": "john",
      "content": "Hello everyone!",
      "created_at": "2025-11-01T10:30:00"
    },
    {
      "id": 2,
      "username": "jane",
      "content": "Hi John!",
      "created_at": "2025-11-01T10:31:15"
    }
  ]
}
```

---

#### **Step 4: React displays messages**

```javascript
// ChatPage.js (React Frontend)
return (
  <div className="messages-list">
    {messages.map((message) => (
      <div key={message.id} className="message">
        <strong>{message.username}</strong>
        <p>{message.content}</p>
        <span>{new Date(message.created_at).toLocaleString()}</span>
      </div>
    ))}
  </div>
);
```

**What this does:**
- `.map()`: Loops through messages array
- `key={message.id}`: React requires unique key for list items
- Returns JSX (looks like HTML, but it's JavaScript)
- React converts this to actual DOM elements

---

### **Example 3: Sending a Message**

#### **Complete Flow:**

```javascript
// FRONTEND (React)
const [newMessage, setNewMessage] = useState('');

const handleSendMessage = async (e) => {
  e.preventDefault();
  
  // 1. Send to backend
  await chatAPI.sendMessage(newMessage);
  
  // 2. Clear input
  setNewMessage('');
  
  // 3. Reload messages
  await loadMessages();
};

// api.js
sendMessage: async (content) => {
  const response = await api.post('/chat/send', { content });
  return response.data;
}
```

```python
# BACKEND (Flask)
@chat_bp.route('/send', methods=['POST'])
def send_message():
    # 1. Get message content
    data = request.get_json()
    message = data.get('content')
    
    # 2. Save to database
    db_service.create_chat_message(username, message)
    # SQL: INSERT INTO messages (username, message, timestamp) VALUES (?, ?, NOW())
    
    # 3. Update Redis cache
    redis_service.increment_message_count(username)
    
    # 4. Queue for async processing
    queue_service.queue_message_processing({
        'username': username,
        'message': message
    })
    
    # 5. Return success
    return jsonify({'success': True}), 201
```

---

## 🔐 **Authentication Flow**

### **How Sessions Work:**

```
1. User logs in
   ↓
2. Flask creates session_id and stores in cookie
   ↓
3. Browser automatically sends cookie with every request
   ↓
4. Flask checks session: if 'username' not in session → 401 Unauthorized
   ↓
5. React receives 401 → redirects to login page
```

**Code:**
```python
# Flask (Backend)
session['username'] = username  # Stores in encrypted cookie

# On subsequent requests:
if 'username' not in session:
    return jsonify({'error': 'Not authenticated'}), 401
```

```javascript
// React (Frontend)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';  // Redirect to login
    }
    return Promise.reject(error);
  }
);
```

---

## 🎨 **React Concepts Explained**

### **1. Components**
Reusable pieces of UI. Like Lego blocks.

```javascript
function LoginPage() {
  return (
    <div>
      <h1>Login</h1>
      <form>...</form>
    </div>
  );
}
```

### **2. State (useState)**
Data that can change. When state changes, React re-renders the component.

```javascript
const [username, setUsername] = useState('');
// username = current value
// setUsername = function to update it

setUsername('john');  // Updates username and re-renders UI
```

### **3. Effects (useEffect)**
Side effects: API calls, timers, subscriptions.

```javascript
useEffect(() => {
  fetchData();  // Runs when component loads
}, []);  // Dependencies: empty = run once
```

### **4. Props**
Data passed from parent to child component.

```javascript
function Message({ username, content }) {
  return <div>{username}: {content}</div>;
}

<Message username="john" content="Hello!" />
```

---

## 🐍 **Flask Concepts Explained**

### **1. Blueprints**
Organize routes by feature.

```python
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    ...

app.register_blueprint(auth_bp, url_prefix='/api/auth')
# Creates route: /api/auth/login
```

### **2. Request Object**
Access HTTP request data.

```python
request.method  # 'GET', 'POST', etc.
request.is_json  # True if Content-Type: application/json
request.get_json()  # Parse JSON body
request.form.get('field')  # Get form data
```

### **3. Session**
Store user-specific data (stored in encrypted cookie).

```python
session['username'] = 'john'  # Set
username = session.get('username')  # Get
session.clear()  # Clear all
```

### **4. JSON Responses**
Return JSON instead of HTML templates.

```python
return jsonify({'success': True, 'data': {...}}), 200
# Converts dict to JSON, sets Content-Type: application/json
```

---

## 🔧 **CORS Explained**

**Problem:** React (localhost:3000) can't call Flask (localhost:5000) - different origins!

**Solution:** Flask-CORS

```python
from flask_cors import CORS

CORS(app, 
     origins=['http://localhost:3000'],  # Allow React
     supports_credentials=True,  # Allow cookies
     methods=['GET', 'POST', 'PUT', 'DELETE'])
```

**What happens:**
```
React sends:
OPTIONS /api/auth/login  (Preflight request)

Flask responds:
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: POST
Access-Control-Allow-Credentials: true

React: "OK, I can proceed with POST request"
```

---

## 📦 **Data Flow Summary**

```
React Component
    ↓ (user action)
API Service (axios)
    ↓ (HTTP request)
Flask Route (@auth_bp.route)
    ↓ (calls)
Database Service (db_service.verify_user)
    ↓ (SQL query)
PostgreSQL Database
    ↓ (returns data)
Database Service
    ↓ (returns user object)
Flask Route (jsonify response)
    ↓ (HTTP response)
API Service (returns data)
    ↓ (updates state)
React Component (re-renders with new data)
    ↓
User sees updated UI
```

---

## 🎯 **Key Differences: Templates vs API**

### **Old Way (Templates):**
```python
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    if verify_user(username):
        return render_template('chat.html')  # Flask sends complete HTML page
```

### **New Way (API):**
```python
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    if verify_user(username):
        return jsonify({'success': True, 'user': {...}})  # Flask sends only data
```

**React builds the UI:**
```javascript
const response = await authAPI.login(username, password);
// React receives JSON and creates HTML in browser
```

---

## ✅ **Benefits of This Architecture**

1. **Separation of Concerns**
   - Frontend: UI/UX logic
   - Backend: Business logic, data management

2. **Better Performance**
   - Only send data, not HTML
   - React updates only what changed

3. **Scalability**
   - Frontend and backend can be deployed separately
   - Can add mobile app using same API

4. **Modern Development**
   - Industry standard approach
   - Easier to maintain and test

---

## 🚀 **Next Steps**

1. Install dependencies: `npm install` in frontend-service
2. Start Flask: `docker-compose up web`
3. Start React: `npm start` in frontend-service
4. Access app: http://localhost:3000
5. Flask API: http://localhost:5000/api

**Remember:** React dev server (port 3000) proxies API calls to Flask (port 5000) automatically!
