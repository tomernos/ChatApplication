# Jenkins Setup Guide - Step 3

## 🎯 Goal
Configure Jenkins to run the golden path pipeline.

## ✅ Prerequisites Verified
- ✅ AWS credentials working
- ✅ S3 bucket and DynamoDB table exist
- ✅ Terraform validated
- ✅ Jenkinsfile exists at: `ChatApplication/Jenkins/Jenkinsfile`

---

## 📋 Step-by-Step Jenkins Configuration

### Part A: Add AWS Credentials (5 minutes)

1. **Open Jenkins UI**
   - Navigate to your Jenkins instance URL
   - Login with your credentials

2. **Navigate to Credentials**
   - Click: **Manage Jenkins** (left sidebar)
   - Click: **Credentials**
   - Click: **System**
   - Click: **Global credentials (unrestricted)**
   - Click: **Add Credentials** (or the domain name if shown)

3. **Configure AWS Credential**
   - **Kind**: Select **AWS Credentials** (from dropdown)
   - **ID**: Type exactly: `aws-creds` (this must match the Jenkinsfile)
   - **Description**: "AWS credentials for ECR, EKS, S3, Terraform"
   - **Access Key ID**: Your AWS access key
   - **Secret Access Key**: Your AWS secret key
   - Click: **OK**

4. **Verify**
   - Credential `aws-creds` should appear in the list
   - ID must be exactly: `aws-creds` (case-sensitive)

---

### Part B: Verify Tools (Optional - 2 minutes)

**If tools are missing, pipeline can use Docker images instead.**

1. **Navigate to Tools**
   - Go to: **Manage Jenkins** → **Global Tool Configuration**

2. **Check Installed Tools**
   - **Docker**: Should be installed (pipeline uses Docker)
   - **AWS CLI**: Optional (can use Docker image)
   - **Terraform**: Optional (can use Docker image)
   - **kubectl**: Optional (can use Docker image)
   - **Helm**: Optional (can use Docker image)

**Note**: The pipeline runs in a Docker container (`python:3.9`), so you can install tools inside the container or use separate Docker images for terraform/kubectl/helm.

---

### Part C: Create Pipeline Job (5 minutes)

1. **Create New Job**
   - On Jenkins home page, click: **New Item** (left sidebar)
   - **Item name**: `chatapp-golden-path` (or your preferred name)
   - **Type**: Select **Pipeline**
   - Click: **OK**

2. **Configure Pipeline**
   - Scroll to **Pipeline** section
   - **Definition**: Select **Pipeline script from SCM**
   - **SCM**: Select **Git**

3. **Configure Git Repository**
   
   **Option 1: If using Git remote (GitHub/GitLab/etc)**:
   - **Repository URL**: Your repository URL
     - Example: `https://github.com/yourusername/ChatApplication.git`
   - **Credentials**: Add if repository is private
   - **Branch Specifier**: `*/develop` (or `*/main`, `*/staging`)

   **Option 2: If using local repository (WSL)**:
   - **Repository URL**: `file:///mnt/c/Users/tomer/Desktop/PersonalGitProjects/ChatApplication`
   - **Branch Specifier**: `*/develop` (or your branch name)

4. **Configure Script Path**
   - **Script Path**: `ChatApplication/Jenkins/Jenkinsfile`
   - (This tells Jenkins where to find the Jenkinsfile in your repo)

5. **Save**
   - Click: **Save** (bottom of page)

6. **Verify**
   - Pipeline job should appear on Jenkins home page
   - Click on it to see configuration

---

## 🚀 Step 4: Run Pipeline

**After Step 3 is complete:**

1. **Open Pipeline Job**
   - Click on `chatapp-golden-path` (or your job name)

2. **Trigger Build**
   - Click: **Build Now** (left sidebar)
   - Or: Push to `develop`/`main`/`staging` branch if webhook configured

3. **Monitor Progress**
   - Click on the build number (#1) in **Build History**
   - Click: **Console Output** to see real-time logs
   - Watch for each stage to complete

4. **Expected Output**
   - All stages should show green checkmarks ✅
   - Console should show:
     - "ECR Registry: 654654526828.dkr.ecr.eu-central-1.amazonaws.com"
     - "Terraform apply completed"
     - "Helm deployment completed"
     - "Health endpoint is responding"

---

## 🆘 Troubleshooting Jenkins Setup

### Credential Not Found
**Error**: "Invalid credentials" in pipeline
**Fix**:
- Verify credential ID is exactly: `aws-creds` (case-sensitive)
- Check credential exists: Manage Jenkins → Credentials → System → Global

### Repository Not Found
**Error**: "Repository not found" or "Could not resolve host"
**Fix**:
- Verify repository URL is correct
- If private repo, add Git credentials in Jenkins
- If local repo, use `file://` path format

### Pipeline Script Not Found
**Error**: "Script not found: ChatApplication/Jenkins/Jenkinsfile"
**Fix**:
- Verify Script Path is: `ChatApplication/Jenkins/Jenkinsfile`
- Check repository structure matches
- Verify branch name is correct

### Tools Not Found
**Error**: "terraform: command not found" or similar
**Fix**:
- Install tools on Jenkins agent, OR
- Modify pipeline to use Docker images with tools
- Example: Use `hashicorp/terraform:latest` Docker image

---

## ✅ Verification Checklist

Before running pipeline, verify:
- [ ] Credential `aws-creds` exists in Jenkins
- [ ] Pipeline job created
- [ ] Repository URL configured correctly
- [ ] Script Path: `ChatApplication/Jenkins/Jenkinsfile`
- [ ] Branch specifier matches your branch

---

## 📝 Quick Reference

**Jenkins Credential**:
- ID: `aws-creds`
- Type: AWS Credentials
- Access Key: [your AWS access key]
- Secret Key: [your AWS secret key]

**Pipeline Configuration**:
- Type: Pipeline script from SCM
- SCM: Git
- Repository: [your repo URL]
- Script Path: `ChatApplication/Jenkins/Jenkinsfile`
- Branch: `*/develop` (or main/staging)

---

## 🎯 Next Action

**Complete Step 3 in Jenkins UI**, then proceed to Step 4 (Run Pipeline).

After pipeline runs successfully, we'll validate the deployment in Step 5.

