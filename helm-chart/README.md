# ConnectHub Helm Chart

A complete Helm chart for deploying ConnectHub - a full-stack chat application with React frontend, Flask backend, PostgreSQL database, Redis cache, and RabbitMQ message queue.

## 🏗️ Architecture

```
┌─────────────┐
│   Frontend  │ (React + Nginx)
│  :30080     │
└──────┬──────┘
       │
       │ HTTP
       ▼
┌─────────────┐     ┌──────────────┐
│   Backend   │────▶│  PostgreSQL  │
│   API       │     │  (Database)  │
│   :5000     │     └──────────────┘
└──────┬──────┘
       │
       ├────▶ Redis (Cache) :6379
       │
       └────▶ RabbitMQ (Queue) :5672
```

## 📦 Components

| Component | Type | Purpose | Default Replicas |
|-----------|------|---------|------------------|
| Frontend | Deployment | React SPA served by Nginx | 2 |
| Backend | Deployment | Flask REST API | 2 |
| PostgreSQL | StatefulSet | Primary database | 1 |
| Redis | Deployment | Cache and sessions | 1 |
| RabbitMQ | Deployment | Message queue | 1 |

## 🚀 Quick Start

### Prerequisites

- Kubernetes cluster (Docker Desktop, Minikube, or cloud)
- Helm 3.x installed
- kubectl configured
- Docker Hub credentials (for private images)

### Installation

```bash
# 1. Create Docker Hub secret (if using private repos)
kubectl create secret docker-registry dockerhub-secret \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=YOUR_USERNAME \
  --docker-password=YOUR_PASSWORD \
  --docker-email=YOUR_EMAIL

# 2. Install the chart
helm install my-connecthub ./helm-chart

# 3. Watch pods come up
kubectl get pods -w
```

### Access the Application

```bash
# Frontend (React app)
open http://localhost:30080

# Backend API health check
kubectl port-forward svc/backend-api 5000:5000
curl http://localhost:5000/health

# RabbitMQ Management UI
kubectl port-forward svc/message-queue 15672:15672
open http://localhost:15672  # guest/guest
```

## ⚙️ Configuration

### Basic Configuration

Edit `values.yaml` or use `--set` flags:

```bash
# Change replica counts
helm install my-connecthub ./helm-chart --set backend.replicas=3

# Update image tags
helm upgrade my-connecthub ./helm-chart \
  --set backend.image.tag=abc123 \
  --set frontend.image.tag=abc123
```

### Key Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `backend.replicas` | Number of backend pods | `2` |
| `backend.image.tag` | Backend Docker image tag | `1b46d09` |
| `frontend.replicas` | Number of frontend pods | `2` |
| `frontend.image.tag` | Frontend Docker image tag | `1b46d09` |
| `postgres.persistence.size` | Database storage size | `1Gi` |
| `redis.enabled` | Enable Redis | `true` |
| `rabbitmq.enabled` | Enable RabbitMQ | `true` |

### Environment-Specific Values

Create environment-specific value files:

```yaml
# values-dev.yaml
backend:
  replicas: 1
  env:
    flaskEnv: "development"

postgres:
  persistence:
    size: 500Mi

# values-prod.yaml
backend:
  replicas: 3
  env:
    flaskEnv: "production"
  
postgres:
  persistence:
    size: 10Gi
```

Deploy with:
```bash
helm install my-connecthub ./helm-chart -f values-dev.yaml
```

## 🔄 Upgrades

```bash
# Upgrade with new image
helm upgrade my-connecthub ./helm-chart --set backend.image.tag=new-tag

# View upgrade history
helm history my-connecthub

# Rollback to previous version
helm rollback my-connecthub

# Rollback to specific revision
helm rollback my-connecthub 3
```

## 🔍 Troubleshooting

### Check Pod Status

```bash
# View all pods
kubectl get pods

# Describe pod (shows events and errors)
kubectl describe pod <pod-name>

# View logs
kubectl logs -f deployment/backend
kubectl logs -f deployment/frontend
```

### Common Issues

**ImagePullBackOff:**
```bash
# Ensure Docker Hub secret exists
kubectl get secret dockerhub-secret

# If missing, recreate it
kubectl create secret docker-registry dockerhub-secret ...
```

**Pods not starting:**
```bash
# Check events
kubectl get events --sort-by='.lastTimestamp'

# Check resource constraints
kubectl top pods
```

**Database connection errors:**
```bash
# Verify PostgreSQL is running
kubectl logs statefulset/postgres

# Check service DNS
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup postgres-service
```

## 🧹 Cleanup

```bash
# Uninstall release (keeps PersistentVolumes)
helm uninstall my-connecthub

# Delete PersistentVolumes manually if needed
kubectl delete pvc postgres-data-postgres-0
```

## 📚 Development

### Testing Changes Locally

```bash
# Lint the chart
helm lint helm-chart/

# Render templates without installing
helm template my-connecthub ./helm-chart

# Dry run (validates against K8s API)
helm install my-connecthub ./helm-chart --dry-run --debug
```

### Packaging

```bash
# Package chart
helm package helm-chart/

# Output: connecthub-1.0.0.tgz
```

## 🔒 Security Notes

⚠️ **Current Implementation:**
- Secrets are hardcoded in templates (OK for learning/development)
- Database passwords in plain text

✅ **Production Recommendations:**
1. Use external secret managers (AWS Secrets Manager, HashiCorp Vault)
2. Enable network policies
3. Use TLS for all connections
4. Implement RBAC properly
5. Scan images for vulnerabilities
6. Use private registries

## 📖 Learn More

- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Chart Development Guide](https://helm.sh/docs/chart_template_guide/)

## 🤝 Contributing

Improvements welcome! Focus areas:
- [ ] Convert hardcoded values to use `values.yaml`
- [ ] Add conditional resource creation (`.Values.xxx.enabled`)
- [ ] Implement proper secret management
- [ ] Add Ingress support
- [ ] Add horizontal pod autoscaling

## 📝 License

MIT License - feel free to use for learning and production!
