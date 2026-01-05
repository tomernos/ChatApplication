# =============================================================================
# Validate Deployment (PowerShell)
# =============================================================================
# This script validates that the application is deployed and running correctly.
#
# What it checks:
#   1. EKS cluster exists and is accessible
#   2. Application pods are running
#   3. Services are created
#   4. Health endpoint responds
#
# Usage:
#   .\validate-deployment.ps1
# =============================================================================

$ErrorActionPreference = "Stop"

# Configuration
$CLUSTER_NAME = "tnt-eu-observability-dev-eks"
$REGION = "eu-central-1"
$NAMESPACE = "chatapp-prod"

function Write-Step {
    param([string]$Message)
    Write-Host "[STEP] $Message" -ForegroundColor Green
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check prerequisites
Write-Step "Checking prerequisites..."
try {
    $null = Get-Command kubectl -ErrorAction Stop
    $null = Get-Command aws -ErrorAction Stop
    Write-Success "Prerequisites check passed"
} catch {
    Write-Error "Required tools not installed (kubectl, aws)"
    exit 1
}
Write-Host ""

# Update kubeconfig
Write-Step "Updating kubeconfig for cluster: $CLUSTER_NAME"
aws eks update-kubeconfig --region $REGION --name $CLUSTER_NAME
if ($LASTEXITCODE -eq 0) {
    Write-Success "Kubeconfig updated"
} else {
    Write-Error "Failed to update kubeconfig"
    exit 1
}
Write-Host ""

# Check cluster access
Write-Step "Checking cluster access..."
kubectl cluster-info | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Cluster is accessible"
} else {
    Write-Error "Cannot access cluster"
    exit 1
}
Write-Host ""

# Check nodes
Write-Step "Checking cluster nodes..."
$nodes = kubectl get nodes --no-headers 2>&1
if ($LASTEXITCODE -eq 0) {
    $nodeCount = ($nodes | Measure-Object -Line).Lines
    Write-Success "Found $nodeCount node(s)"
    kubectl get nodes
} else {
    Write-Error "No nodes found in cluster"
    exit 1
}
Write-Host ""

# Check namespace
Write-Step "Checking namespace: $NAMESPACE"
kubectl get namespace $NAMESPACE | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Namespace exists"
} else {
    Write-Error "Namespace does not exist"
    exit 1
}
Write-Host ""

# Check pods
Write-Step "Checking application pods..."
$pods = kubectl get pods -n $NAMESPACE --no-headers 2>&1
if ($LASTEXITCODE -eq 0) {
    $podCount = ($pods | Measure-Object -Line).Lines
    Write-Success "Found $podCount pod(s)"
    kubectl get pods -n $NAMESPACE
    
    $failedPods = kubectl get pods -n $NAMESPACE --no-headers 2>&1 | 
        Where-Object { $_ -notmatch "Running|Completed" }
    if ($failedPods) {
        Write-Warning "Some pods are not running:"
        $failedPods
    }
} else {
    Write-Error "No pods found in namespace"
    exit 1
}
Write-Host ""

# Check services
Write-Step "Checking services..."
$services = kubectl get svc -n $NAMESPACE --no-headers 2>&1
if ($LASTEXITCODE -eq 0) {
    $svcCount = ($services | Measure-Object -Line).Lines
    Write-Success "Found $svcCount service(s)"
    kubectl get svc -n $NAMESPACE
} else {
    Write-Warning "No services found"
}
Write-Host ""

# Test health endpoint
Write-Step "Testing health endpoint..."
$backendSvc = kubectl get svc -n $NAMESPACE -o jsonpath='{.items[?(@.metadata.name=="chatapp-backend")].metadata.name}' 2>&1

if ($backendSvc) {
    Write-Step "Port-forwarding to backend service..."
    Start-Process -NoNewWindow kubectl -ArgumentList "port-forward", "-n", $NAMESPACE, "svc/$backendSvc", "5000:5000"
    Start-Sleep -Seconds 5
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "Health endpoint is responding"
            $response.Content | Select-Object -First 5
        }
    } catch {
        Write-Error "Health endpoint is not responding"
        Get-Process kubectl | Where-Object { $_.CommandLine -like "*port-forward*" } | Stop-Process -Force -ErrorAction SilentlyContinue
        exit 1
    }
    
    Get-Process kubectl | Where-Object { $_.CommandLine -like "*port-forward*" } | Stop-Process -Force -ErrorAction SilentlyContinue
} else {
    Write-Warning "Backend service not found, skipping health check"
}
Write-Host ""

Write-Host "============================================================================="
Write-Success "Deployment validation completed!"
Write-Host "============================================================================="
Write-Host ""
Write-Host "Summary:"
Write-Host "  - Cluster: $CLUSTER_NAME"
Write-Host "  - Namespace: $NAMESPACE"
Write-Host "  - Nodes: $nodeCount"
Write-Host "  - Pods: $podCount"
Write-Host "  - Services: $svcCount"
Write-Host ""

