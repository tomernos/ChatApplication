# Jenkins Pipelines

## Directory Structure

```
Jenkins/
├── legacy/          # Legacy pipelines (deployments/ directory method)
│   ├── Jenkinsfile.ci
│   └── Jenkinsfile.cd
├── gitops/          # GitOps pipelines (CompanyGitOps repo method)
│   ├── Jenkinsfile.ci
│   └── Jenkinsfile.cd
└── README.md        # This file
```

## Pipeline Separation

### Legacy Pipelines (`legacy/`)

**Purpose**: Original deployment method using `deployments/` directory in ChatApplication repo.

**CI Pipeline** (`legacy/Jenkinsfile.ci`):
- Builds Docker images
- Pushes to ECR
- Updates `deployments/{env}/deployment.yaml` in ChatApplication repo
- No GitOps repository updates

**CD Pipeline** (`legacy/Jenkinsfile.cd`):
- Reads from `deployments/{env}/deployment.yaml`
- Uses local Helm values files (`values-{env}.yaml`)
- No GitOps repository access

**Use Case**: 
- Existing deployments that haven't migrated
- Simple single-repo deployments
- When GitOps repo is not available

---

### GitOps Pipelines (`gitops/`)

**Purpose**: Modern GitOps method using separate CompanyGitOps repository.

**CI Pipeline** (`gitops/Jenkinsfile.ci`):
- Builds Docker images
- Pushes to ECR
- Updates `CompanyGitOps/applications/chatapp/{env}/deployment.yaml`
- No local `deployments/` directory updates

**CD Pipeline** (`gitops/Jenkinsfile.cd`):
- Reads from `CompanyGitOps/applications/chatapp/{env}/deployment.yaml`
- Uses values files from GitOps repo (`applications/chatapp/{env}/values.yaml`)
- No legacy fallback

**Use Case**:
- Company-wide GitOps deployments
- Multi-application management
- Separation of concerns (app code vs deployment config)
- ArgoCD/Flux integration ready

---

## Key Differences

| Feature | Legacy | GitOps |
|---------|-------|--------|
| Deployment Manifest | `deployments/{env}/deployment.yaml` | `CompanyGitOps/applications/chatapp/{env}/deployment.yaml` |
| Values Files | Local `values-{env}.yaml` | GitOps repo `values.yaml` |
| Repository | ChatApplication repo | CompanyGitOps repo |
| Fallback | N/A | N/A (pure method) |
| Multi-App Support | No | Yes |
| Separation of Concerns | No | Yes |

---

## Migration Path

1. **Current**: Both methods work independently
2. **Choose Method**: 
   - Use `legacy/` for simple deployments
   - Use `gitops/` for company-wide GitOps
3. **Configure Jenkins**: Point Jenkins jobs to chosen pipeline directory

---

## Configuration

### Legacy Pipelines
- No additional configuration needed
- Uses `deployments/` directory in ChatApplication repo

### GitOps Pipelines
- Requires `CompanyGitOps` repository access
- Set `GIT_CREDENTIALS_ID` in Jenkins credentials
- Ensure GitOps repo structure exists:
  ```
  CompanyGitOps/
  └── applications/
      └── chatapp/
          ├── dev/
          │   ├── deployment.yaml
          │   └── values.yaml
          ├── staging/
          └── prod/
  ```

---

## Best Practices

1. **Choose One Method**: Don't mix legacy and GitOps for the same application
2. **Consistent Structure**: Follow GitOps repo structure for new applications
3. **Version Control**: Both methods use Git for version tracking
4. **Documentation**: Update this README when adding new applications

---

## Troubleshooting

### Legacy Pipeline Issues
- Check `deployments/{env}/deployment.yaml` exists
- Verify Git credentials for ChatApplication repo
- Ensure CI has run and updated deployment manifest

### GitOps Pipeline Issues
- Verify GitOps repo access (`GIT_CREDENTIALS_ID`)
- Check GitOps repo structure matches expected format
- Ensure CI has updated GitOps repo deployment.yaml
- Verify values.yaml exists in GitOps repo
