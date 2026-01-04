# Jenkins Credentials Setup

This document lists all required Jenkins credentials for the CI/CD pipeline.

## Required Credentials

### 1. AWS Credentials (`aws-creds`)
- **Credential ID**: `aws-creds`
- **Type**: AWS Credentials (Access Key ID + Secret Access Key)
- **Required Permissions**:
  - EKS cluster access (read/write)
  - ECR repository access (push/pull images)
  - S3 bucket access (for Terraform state)
  - DynamoDB access (for Terraform state locking)
  - IAM permissions to update kubeconfig
- **Setup Instructions**:
  1. Go to Jenkins → Manage Jenkins → Credentials
  2. Add new credential → AWS Credentials
  3. Set ID: `aws-creds`
  4. Enter AWS Access Key ID and Secret Access Key
  5. Save

### 2. Docker Hub Credentials (`dockerhubauth`)
- **Credential ID**: `dockerhubauth`
- **Type**: Username with Password
- **Required Permissions**:
  - Push/pull images to Docker Hub registry
- **Setup Instructions**:
  1. Go to Jenkins → Manage Jenkins → Credentials
  2. Add new credential → Username with password
  3. Set ID: `dockerhubauth`
  4. Enter Docker Hub username and password (or access token)
  5. Save

### 3. GitHub Personal Access Token (`gitpat`)
- **Credential ID**: `gitpat`
- **Type**: Username with Password (username = GitHub username, password = PAT)
- **Required Permissions**:
  - `repo` scope (full repository access)
  - `workflow` scope (if using GitHub Actions)
- **Purpose**: Used for pushing Git tags created during semantic versioning
- **Setup Instructions**:
  1. Generate GitHub PAT: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
  2. Create token with `repo` scope
  3. Go to Jenkins → Manage Jenkins → Credentials
  4. Add new credential → Username with password
  5. Set ID: `gitpat`
  6. Username: Your GitHub username
  7. Password: Your GitHub PAT
  8. Save

## Verification

After setting up credentials, verify they work:

```groovy
// Test AWS credentials
withCredentials([[
    $class: 'AmazonWebServicesCredentialsBinding',
    credentialsId: 'aws-creds',
    accessKeyVariable: 'AWS_ACCESS_KEY_ID',
    secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
]]) {
    sh 'aws sts get-caller-identity'
}

// Test Docker Hub credentials
withCredentials([usernamePassword(
    credentialsId: 'dockerhubauth',
    usernameVariable: 'DOCKER_USER',
    passwordVariable: 'DOCKER_PASS'
)]) {
    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
}

// Test GitHub credentials
withCredentials([usernamePassword(
    credentialsId: 'gitpat',
    usernameVariable: 'GIT_USERNAME',
    passwordVariable: 'GIT_PASSWORD'
)]) {
    sh 'curl -u $GIT_USERNAME:$GIT_PASSWORD https://api.github.com/user'
}
```

## Security Notes

- Never commit credentials to version control
- Rotate credentials regularly
- Use least-privilege IAM policies for AWS credentials
- Use GitHub PATs with minimal required scopes
- Consider using Jenkins credential rotation plugins

