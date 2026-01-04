# Pipeline Separation - Separation of Concerns

## 🎯 Overview

The CI/CD pipeline has been separated into three distinct pipelines following separation of concerns:

1. **CI Pipeline** (`Jenkinsfile.ci`) - Build, Test, Push to ECR
2. **Infrastructure Pipeline** (`Jenkinsfile.infrastructure`) - Terraform provisioning
3. **CD Pipeline** (`Jenkinsfile.cd`) - Deploy to Kubernetes

---

## 📋 Pipeline Details

### 1. CI Pipeline (`Jenkinsfile.ci`)

**Purpose**: Continuous Integration - Build, test, and publish artifacts

**Stages**:
- Checkout
- Calculate & Create Version Tag
- Setup Dependencies
- Python Tests
- Build Docker Images (Backend + Frontend in parallel)
- Tag Images
- Authenticate to AWS & Set ECR Registry
- Push to ECR
- Archive Artifacts

**Triggers**: 
- On push to `develop`, `staging`, `main` branches
- Manual trigger

**Outputs**:
- Docker images pushed to ECR
- Versioned artifacts
- Build manifest

**When to run**: On every code change

---

### 2. Infrastructure Pipeline (`Jenkinsfile.infrastructure`)

**Purpose**: Provision and manage AWS infrastructure via Terraform

**Stages**:
- Checkout
- Install Tools (AWS CLI, Terraform)
- Terraform Init (with S3 backend)
- Terraform Validate
- Terraform Plan
- Terraform Apply (only on main/develop/staging)
- Verify Infrastructure

**Triggers**:
- Manual trigger (recommended)
- On infrastructure code changes
- Scheduled runs for drift detection

**Outputs**:
- EKS cluster
- VPC, subnets, security groups
- IAM roles and policies
- ECR repositories (if not exists)
- Route53 zones
- Other infrastructure resources

**When to run**: 
- Initial infrastructure setup
- Infrastructure changes
- Periodic drift detection

**⚠️ Important**: Run this pipeline BEFORE CD pipeline to ensure infrastructure exists.

---

### 3. CD Pipeline (`Jenkinsfile.cd`)

**Purpose**: Continuous Deployment - Deploy application to Kubernetes

**Stages**:
- Checkout
- Install Tools (kubectl, Helm, AWS CLI)
- Authenticate to AWS
- Configure Kubeconfig
- Helm Deploy Application
- Post-Deployment Smoke Tests

**Parameters**:
- `IMAGE_VERSION`: Docker image version to deploy (default: latest)
- `ECR_REGISTRY_PARAM`: ECR registry URL (default: auto-detect from AWS)

**Triggers**:
- Manual trigger (recommended - after CI pipeline completes)
- Can be triggered after successful CI pipeline
- On-demand deployment

**Outputs**:
- Application deployed to Kubernetes
- Health checks verified

**When to run**: 
- After CI pipeline successfully pushes images to ECR
- When deploying a specific version
- For rollbacks

---

## 🔄 Pipeline Workflow

### Recommended Execution Order:

```
1. Infrastructure Pipeline (one-time or when infra changes)
   ↓
2. CI Pipeline (on every code change)
   ↓
3. CD Pipeline (after CI completes, deploy new version)
```

### Typical Workflow:

1. **Developer pushes code** → Triggers CI Pipeline
2. **CI Pipeline**:
   - Builds and tests code
   - Pushes images to ECR with version tag
   - Archives artifacts
3. **After CI succeeds** → Manually trigger CD Pipeline (or automate)
4. **CD Pipeline**:
   - Pulls images from ECR
   - Deploys to Kubernetes via Helm
   - Runs smoke tests

---

## 🚀 Setup Instructions

### Step 1: Create Jenkins Jobs

Create three separate Jenkins pipeline jobs:

#### Job 1: `chatapp-ci`
- **Type**: Pipeline
- **Pipeline script from SCM**: Git
- **Repository**: Your repo URL
- **Branch**: `*/develop` (or main/staging)
- **Script Path**: `ChatApplication/Jenkins/Jenkinsfile.ci`

#### Job 2: `chatapp-infrastructure`
- **Type**: Pipeline
- **Pipeline script from SCM**: Git
- **Repository**: Your repo URL
- **Branch**: `*/develop` (or main/staging)
- **Script Path**: `ChatApplication/Jenkins/Jenkinsfile.infrastructure`

#### Job 3: `chatapp-cd`
- **Type**: Pipeline
- **Pipeline script from SCM**: Git
- **Repository**: Your repo URL
- **Branch**: `*/develop` (or main/staging)
- **Script Path**: `ChatApplication/Jenkins/Jenkinsfile.cd`

---

### Step 2: Configure Credentials

All pipelines need:
- `aws-creds` (Username/Password) - AWS credentials
- `gitpat` (Username/Password) - GitHub PAT (for CI pipeline only)

---

### Step 3: Execution Order

1. **First Time Setup**:
   ```
   Run Infrastructure Pipeline → Creates EKS cluster and resources
   ```

2. **Regular Development**:
   ```
   Run CI Pipeline → Builds and pushes images
   Run CD Pipeline → Deploys to cluster
   ```

---

## 📊 Benefits of Separation

1. **Separation of Concerns**: Each pipeline has a single responsibility
2. **Independent Execution**: Run pipelines independently
3. **Better Security**: Infrastructure changes require explicit approval
4. **Easier Debugging**: Isolate issues to specific pipeline
5. **Flexible Deployment**: Deploy specific versions without rebuilding
6. **Resource Efficiency**: Don't run expensive operations unnecessarily

---

## 🔗 Pipeline Dependencies

- **CD Pipeline** depends on:
  - Infrastructure Pipeline (cluster must exist)
  - CI Pipeline (images must be in ECR)

- **CI Pipeline** is independent (can run anytime)

- **Infrastructure Pipeline** is independent (run when needed)

---

## 📝 Notes

- The original `Jenkinsfile` is kept for reference but should not be used
- Each pipeline can be run independently
- CD pipeline accepts parameters for flexible deployment
- Infrastructure pipeline only applies on main/develop/staging branches

---

## 🆘 Troubleshooting

### CD Pipeline fails: "cluster not found"
→ Run Infrastructure Pipeline first

### CD Pipeline fails: "image not found in ECR"
→ Run CI Pipeline first to push images

### CI Pipeline fails: "ECR_REGISTRY is null"
→ Check AWS credentials and region configuration

---

## ✅ Next Steps

1. Create the three Jenkins jobs as described above
2. Run Infrastructure Pipeline (one-time setup)
3. Run CI Pipeline (build and push images)
4. Run CD Pipeline (deploy application)

