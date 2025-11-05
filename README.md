# ConnectHub Chat Application

Modern chat application with React frontend and Flask API backend, ready for Kubernetes deployment.

## 🏗️ **Architecture**

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

```
ChatApplication/
├── app/                      # Flask backend API
│   ├── routes/              # API endpoints (auth, chat, users)
│   ├── services/            # Business logic (database, redis, queue)
│   └── models/              # Database models
├── frontend-service/         # React frontend
│   ├── src/
│   │   ├── pages/           # React pages (Login, Chat, Profile, etc.)
│   │   ├── services/        # API client (axios)
│   │   └── styles/          # CSS files
│   ├── public/              # Static files
│   └── Dockerfile           # Frontend container (Nginx)
├── docker-compose.yml        # Multi-container orchestration
├── Dockerfile               # Backend container
└── requirements.txt          # Python dependencies
```

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

## 📦 **Production Deployment**

### **Build Images**
```bash
# Backend
docker build -t connecthub-backend:latest .

# Frontend
cd frontend-service
docker build -t connecthub-frontend:latest .
```

### **Run in Production**
```bash
# Set environment variables
export DATABASE_URL=postgresql://user:pass@host:5432/db
export REDIS_URL=redis://host:6379/0

# Run backend
docker run -p 5000:5000 -e DATABASE_URL=$DATABASE_URL connecthub-backend:latest

# Run frontend
docker run -p 3000:80 connecthub-frontend:latest
```

## 🧪 **Testing**

```bash
# Run backend tests
pytest

# Run frontend tests
cd frontend-service
npm test
```

## 🔒 **Security Features**

- ✅ CORS configured for frontend-backend communication
- ✅ Session management with Flask sessions
- ✅ Password hashing (database level)
- ✅ SQL injection protection (parameterized queries)
- ✅ Input validation on all endpoints

## 📊 **Monitoring**

- Structured logging with timestamps
- Health check endpoints for Kubernetes
- Ready probe checks database connectivity
- Error tracking in logs

## 🎯 **Next Steps (DevOps Journey)**

1. **Kubernetes Deployment**
   - Create K8s manifests (deployments, services, ingress)
   - Deploy to Minikube/Kind locally
   - Deploy to cloud (EKS, GKE, AKS)

2. **Helm Charts**
   - Package application for easy deployment
   - Manage different environments (dev, staging, prod)

3. **CI/CD Pipeline**
   - Automated testing
   - Build Docker images
   - Deploy to Kubernetes
   - GitOps with ArgoCD

4. **Infrastructure as Code**
   - Terraform for cloud resources
   - Provision Kubernetes clusters
   - Manage databases, networking

5. **Monitoring & Observability**
   - Prometheus metrics
   - Grafana dashboards
   - ELK stack for logs
   - Distributed tracing

## 📝 **License**

MIT License - Learning project for DevOps best practices
