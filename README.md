# ConnectHub Chat Application

chat application with React frontend and Flask API backend.

## 🏗️ **Architecture**
test
```
┌─────────────────┐         ┌──────────────────┐
│  React Frontend │────────>│   Flask API      │
│  (Port 3000)    │  JSON   │   (Port 5000)    │
└─────────────────┘         └──────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
              ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
              │ PostgreSQL│   │   Redis   │   │ RabbitMQ  │
              │ (Port5432)│   │ (Port6379)│   │ (Port5672)│
              └───────────┘   └───────────┘   └───────────┘
```

## 📁 **Project Structure**


## 🚀 **Quick Start**

### **Option 1: Run with Docker (Recommended)**

```bash
# Start all services
docker-compose up --build

# Access application
Frontend: http://localhost:3000
Backend API: http://localhost:5000
API Docs: http://localhost:5000/
```

### **Option 2: Development Mode (React + Flask separate)**

Terminal 1 - Backend:
```bash
docker-compose up web postgres redis rabbitmq
```

Terminal 2 - Frontend:
```bash
cd frontend-service
npm install
npm start
```

## 🔌 **API Endpoints**

### **Health Checks** (Kubernetes ready)
- `GET /health` - Liveness probe
- `GET /ready` - Readiness probe (checks DB connection)

### **Authentication**
- `POST /api/auth/register` - Create new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/profile` - Get current user

### **Chat**
- `GET /api/chat/messages` - Get all messages
- `POST /api/chat/send` - Send new message
- `DELETE /api/chat/message/<id>` - Delete message

### **Users**
- `GET /api/users` - Get all users
- `GET /api/users/<id>` - Get specific user
- `PUT /api/users/<id>` - Update user
- `DELETE /api/users/<id>` - Delete user

## 🛠️ **Technologies**

### **Frontend**
- React 18
- React Router (client-side routing)
- Axios (HTTP client)
- Nginx (production web server)

### **Backend**
- Flask 2.0 (Python web framework)
- SQLAlchemy (ORM)
- PostgreSQL (database)
- Redis (caching, sessions)
- RabbitMQ (message queue)
- Gunicorn (production WSGI server)
