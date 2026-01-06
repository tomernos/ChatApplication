# Deployment Promotion Strategy

## Build Once, Promote Across Environments

This directory implements the enterprise-grade "build once, promote" pattern.

### Architecture

```
develop branch (CI)
  ↓ Build artifact v2.2.0-dev.1 → ECR
  ↓ Update deployments/dev/deployment.yaml
  
dev branch (CD)
  ↓ Read version from deployments/dev/deployment.yaml
  ↓ Deploy v2.2.0-dev.1 to EKS dev namespace
  
staging branch (CD)
  ↓ Read version from deployments/staging/deployment.yaml
  ↓ Deploy v2.2.0-dev.1 to EKS staging namespace (after promotion)
  
prod branch (CD)
  ↓ Read version from deployments/prod/deployment.yaml
  ↓ Deploy v2.2.0-dev.1 to EKS prod namespace (after promotion + approval)
```

### Promotion Process

1. **CI builds on `develop`**:
   - Builds artifact once
   - Tags with semantic version
   - Pushes to ECR
   - Updates `deployments/dev/deployment.yaml` with new version

2. **Auto-deploy to dev**:
   - CD pipeline on `dev` branch reads version from `deployments/dev/deployment.yaml`
   - Deploys automatically (no rebuild)

3. **Promote to staging**:
   - Copy version from `deployments/dev/deployment.yaml` → `deployments/staging/deployment.yaml`
   - Commit to `staging` branch
   - CD pipeline deploys same artifact

4. **Promote to prod**:
   - Copy version from `deployments/staging/deployment.yaml` → `deployments/prod/deployment.yaml`
   - Commit to `prod` branch
   - CD pipeline requires approval, then deploys same artifact

### File Structure

```
deployments/
├── dev/
│   └── deployment.yaml      # Version deployed to dev
├── staging/
│   └── deployment.yaml      # Version deployed to staging
└── prod/
    └── deployment.yaml      # Version deployed to prod
```

### Benefits

- ✅ Same artifact across all environments (no rebuild)
- ✅ Traceable promotion (Git history)
- ✅ Rollback by reverting deployment.yaml
- ✅ Environment-specific configs possible
- ✅ Simulates enterprise workflow

