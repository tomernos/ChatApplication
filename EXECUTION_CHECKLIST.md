# Golden Path Execution Checklist

## ✅ Pre-Execution (All Agents Complete)

- [x] INFRA-TF AGENT: Terraform outputs verified
- [x] CI/CD AGENT: Jenkinsfile fixed and validated
- [x] APP-DEPLOY AGENT: Helm chart verified

---

## 📋 Execution Steps

### Step 1: Bootstrap State Backend
- [ ] Run bootstrap script (Windows: `.ps1`, Linux/Mac: `.sh`)
- [ ] Verify S3 bucket created: `tnt-eu-observability-dev-tf`
- [ ] Verify DynamoDB table created: `tnt-eu-observability-dev-tf-locks`
- [ ] Script reports success

**Command**:
```bash
cd Observability/infra-tf/scripts
./bootstrap-state.sh  # or .ps1 on Windows
```

**Time**: 5 minutes

---

### Step 2: Validate Terraform
- [ ] Run validation script
- [ ] Terraform init succeeds
- [ ] Terraform validate passes
- [ ] Terraform plan shows resources

**Command**:
```bash
cd Observability/infra-tf/scripts
./validate-terraform.sh  # or .ps1 on Windows
```

**Time**: 3 minutes

---

### Step 3: Configure Jenkins

#### 3.1: AWS Credentials
- [ ] Open Jenkins UI
- [ ] Navigate to: Manage Jenkins → Credentials → System → Global
- [ ] Add credential:
  - ID: `aws-creds`
  - Type: AWS Credentials
  - Access Key ID: [your key]
  - Secret Access Key: [your secret]
- [ ] Save credential

#### 3.2: Verify Tools
- [ ] Go to: Manage Jenkins → Global Tool Configuration
- [ ] Verify installed:
  - [ ] Docker
  - [ ] AWS CLI (or Docker image)
  - [ ] Terraform (or Docker image)
  - [ ] kubectl (or Docker image)
  - [ ] Helm (or Docker image)

#### 3.3: Create Pipeline Job
- [ ] Click: New Item
- [ ] Name: `chatapp-golden-path`
- [ ] Type: Pipeline
- [ ] Configure:
  - [ ] Pipeline script from SCM
  - [ ] SCM: Git
  - [ ] Repository URL: [your repo]
  - [ ] Branch: `*/develop` (or main/staging)
  - [ ] Script Path: `ChatApplication/Jenkins/Jenkinsfile`
- [ ] Save

**Time**: 10 minutes

---

### Step 4: Run Pipeline

#### 4.1: Trigger
- [ ] Open pipeline job
- [ ] Click: Build Now
- [ ] Monitor build progress

#### 4.2: Monitor Stages
- [ ] Checkout ✅
- [ ] Calculate Version ✅
- [ ] Build Images ✅
- [ ] Authenticate to AWS ✅ (verify ECR_REGISTRY is set)
- [ ] Push to ECR ✅
- [ ] Terraform Apply ✅
- [ ] Configure Kubeconfig ✅
- [ ] Helm Deploy ✅
- [ ] Smoke Tests ✅

#### 4.3: Check Console
- [ ] ECR Registry shown: `123456789.dkr.ecr.eu-central-1.amazonaws.com`
- [ ] Terraform apply: "Apply complete!"
- [ ] Helm deploy: "Release has been upgraded"
- [ ] Smoke tests: "Health endpoint is responding"

**Time**: 15-30 minutes

---

### Step 5: Validate Deployment
- [ ] Run validation script
- [ ] Or manually:
  - [ ] `aws eks update-kubeconfig --region eu-central-1 --name tnt-eu-observability-dev-eks`
  - [ ] `kubectl get nodes` (shows 2+ nodes)
  - [ ] `kubectl get pods -n chatapp-prod` (shows running pods)
  - [ ] `kubectl port-forward -n chatapp-prod svc/chatapp-backend 5000:5000`
  - [ ] `curl http://localhost:5000/health` (returns 200 OK)

**Command**:
```bash
cd ChatApplication/Jenkins/scripts
./validate-deployment.sh  # or .ps1 on Windows
```

**Time**: 5 minutes

---

## ✅ Final Verification

- [ ] S3 bucket exists
- [ ] DynamoDB table exists
- [ ] Terraform state in S3
- [ ] EKS cluster exists
- [ ] Application pods running
- [ ] Health endpoint responds
- [ ] Pipeline runs end-to-end

---

## 🎉 Success!

**If all checkboxes are checked**: You've completed the AWS golden path!

**Next**: Document your achievements and move to observability/alerting phase.

---

## 📝 Notes

- Keep this checklist open while executing
- Check off items as you complete them
- If any step fails, check troubleshooting in `NEXT_STEPS_EXECUTION.md`
- Total estimated time: 35-55 minutes

