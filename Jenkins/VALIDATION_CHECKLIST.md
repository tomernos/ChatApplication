# Pipeline Validation Checklist

This checklist helps verify the CI/CD pipeline is ready for execution.

## Pre-Pipeline Checks

### ✅ Jenkins Configuration
- [ ] Jenkins shared library is configured (`jenkins-shared-library`)
- [ ] All required credentials are set up (see `CREDENTIALS_SETUP.md`)
- [ ] Jenkins has Docker socket access (`/var/run/docker.sock`)
- [ ] Required Jenkins plugins installed:
  - Pipeline plugin
  - Docker Pipeline plugin
  - AWS Steps plugin
  - Credentials Binding plugin
  - Timestamper plugin

### ✅ Tools Available in Pipeline
- [ ] Python 3.9 (via Docker image)
- [ ] Docker CLI
- [ ] Docker Compose v2
- [ ] Terraform CLI
- [ ] Helm CLI
- [ ] kubectl CLI
- [ ] AWS CLI
- [ ] curl
- [ ] git

### ✅ AWS Resources
- [ ] EKS cluster exists: `tnt-eu-observability-dev-eks`
- [ ] ECR repositories exist (will be auto-created if missing):
  - `connecthub-backend`
  - `connecthub-frontend`
- [ ] AWS credentials have required permissions (see `ECR_SETUP.md`)
- [ ] Terraform state bucket exists (if using Terraform)
- [ ] ECR_REGISTRY will be set automatically from AWS account ID

### ✅ Code Repository
- [ ] Repository is accessible from Jenkins
- [ ] Branch protection rules configured (if applicable)
- [ ] Webhooks configured (if using automatic triggers)

## Expected Pipeline Stages

The pipeline executes these stages in order:

1. **Checkout** - Clone repository
2. **Calculate & Create Version Tag** - Semantic versioning
3. **Setup Dependencies** - Install system packages, Python deps, Docker Compose
4. **Python Tests** - Run backend tests (if not skipped)
5. **Build Docker Images** - Build backend and frontend in parallel
6. **Tag Images** - Tag for docker-compose
7. **Start Services** - Start services with docker-compose
8. **Integration Health Checks Test** - Verify services are healthy
9. **Archive Artifacts** - Save build artifacts
10. **Push to Docker Hub** - Push images (if enabled and on main/staging/develop)
11. **Authenticate to AWS & Set ECR Registry** - Set ECR_REGISTRY from AWS account (if on main/staging/develop)
12. **Push to ECR** - Push images to ECR, auto-create repositories (if on main/staging/develop)
13. **Terraform Apply** - Ensure EKS cluster exists (if on main/staging/develop)
14. **Configure Kubeconfig** - Set up kubectl for EKS (if on main/staging/develop)
15. **Helm Deploy Application** - Deploy to Kubernetes (if on main/staging/develop)
16. **Deploy to Dev/Staging/Production** - Environment-specific deployment
17. **Post-Deployment Smoke Tests** - Verify deployment

## Post-Pipeline Validation Commands

After pipeline completes successfully, verify deployment:

```bash
# Verify Kubernetes deployment
kubectl get deployments -n chatapp-prod
kubectl get pods -n chatapp-prod
kubectl get services -n chatapp-prod

# Check pod logs
kubectl logs -n chatapp-prod deployment/chatapp-backend --tail=50
kubectl logs -n chatapp-prod deployment/chatapp-frontend --tail=50

# Test health endpoint
kubectl port-forward -n chatapp-prod svc/chatapp-backend 5000:5000 &
curl http://localhost:5000/health

# Verify Helm release
helm list -n chatapp-prod
helm get values chatapp -n chatapp-prod
```

## Troubleshooting Common Errors

### Error: "Shared library not found"
- **Solution**: Configure shared library in Jenkins → Manage Jenkins → Configure System → Global Pipeline Libraries
- Set name: `jenkins-shared-library`
- Set repository URL and credentials

### Error: "Credentials not found"
- **Solution**: Verify credential IDs match exactly:
  - `aws-creds` for AWS
  - `dockerhubauth` for Docker Hub
  - `gitpat` for GitHub
- Check credential types match (AWS Credentials vs Username/Password)

### Error: "ECR_REGISTRY is empty"
- **Status**: ✅ FIXED - ECR_REGISTRY is now set automatically in "Authenticate to AWS & Set ECR Registry" stage
- **Verification**: Check pipeline logs for "Authenticate to AWS" stage output:
  - Should show: "ECR Registry: {accountId}.dkr.ecr.{region}.amazonaws.com"
- **If still failing**: 
  - Verify "Authenticate to AWS & Set ECR Registry" stage runs before "Push to ECR" and "Helm Deploy"
  - Check AWS credentials have `sts:GetCallerIdentity` permission
  - Verify AWS_REGION environment variable is set correctly

### Error: "Terraform init fails"
- **Solution**: 
  - Verify S3 bucket exists for Terraform state
  - Verify DynamoDB table exists for state locking
  - Run bootstrap script: `cd Observability/infra-tf/scripts && ./bootstrap-state.sh`

### Error: "kubectl: command not found"
- **Solution**: Install kubectl in Jenkins agent or use Docker image with kubectl

### Error: "Helm: command not found"
- **Solution**: Install Helm in Jenkins agent or use Docker image with Helm

### Error: "Docker daemon not accessible"
- **Solution**: 
  - Verify Docker socket is mounted: `-v /var/run/docker.sock:/var/run/docker.sock`
  - Check Jenkins agent has permission to access Docker socket

### Error: "Health check failed"
- **Solution**:
  - Check pod logs: `kubectl logs -n chatapp-prod deployment/chatapp-backend`
  - Verify service is running: `kubectl get pods -n chatapp-prod`
  - Check service endpoints: `kubectl get endpoints -n chatapp-prod`
  - Verify health endpoint exists: `curl http://localhost:5000/health`

## Success Criteria

Pipeline is successful when:
- ✅ All stages complete without errors
- ✅ Docker images are built and tagged
- ✅ Services start and pass health checks
- ✅ Images are pushed to registry (if enabled)
- ✅ Kubernetes deployment is successful
- ✅ Smoke tests pass
- ✅ No failed stages in pipeline console

## ECR_REGISTRY Validation

The pipeline automatically sets `ECR_REGISTRY` in the "Authenticate to AWS & Set ECR Registry" stage. To verify:

1. **Check pipeline stage output**:
   - Look for "Authenticate to AWS & Set ECR Registry" stage
   - Should show: "ECR Registry: {accountId}.dkr.ecr.{region}.amazonaws.com"

2. **Verify in subsequent stages**:
   - "Push to ECR" stage validates ECR_REGISTRY is set
   - "Helm Deploy Application" stage validates ECR_REGISTRY is set
   - Both will fail fast with clear error if ECR_REGISTRY is empty

3. **Manual verification** (if needed):
   ```bash
   # In Jenkins pipeline script console or stage:
   echo "ECR_REGISTRY: ${env.ECR_REGISTRY}"
   # Should output: 123456789012.dkr.ecr.eu-central-1.amazonaws.com
   ```

## Related Documentation

- [ECR_SETUP.md](./ECR_SETUP.md) - ECR repository setup and configuration
- [CREDENTIALS_SETUP.md](./CREDENTIALS_SETUP.md) - Jenkins credentials setup
- [AWS ECR User Guide](https://docs.aws.amazon.com/ecr/)
- [Jenkins AWS Plugin](https://plugins.jenkins.io/aws-credentials/)

