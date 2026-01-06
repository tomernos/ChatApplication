#!/bin/bash

# =============================================================================
# Validate Deployment
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
#   chmod +x validate-deployment.sh
#   ./validate-deployment.sh
# =============================================================================

set -e

# Configuration
CLUSTER_NAME="tnt-eu-observability-dev-eks"
REGION="eu-central-1"
NAMESPACE="chatapp-prod"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
print_step "Checking prerequisites..."
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed"
    exit 1
fi

print_success "Prerequisites check passed"
echo ""

# Update kubeconfig
print_step "Updating kubeconfig for cluster: $CLUSTER_NAME"
if aws eks update-kubeconfig --region "$REGION" --name "$CLUSTER_NAME"; then
    print_success "Kubeconfig updated"
else
    print_error "Failed to update kubeconfig"
    exit 1
fi
echo ""

# Check cluster access
print_step "Checking cluster access..."
if kubectl cluster-info &> /dev/null; then
    print_success "Cluster is accessible"
else
    print_error "Cannot access cluster"
    exit 1
fi
echo ""

# Check nodes
print_step "Checking cluster nodes..."
NODES=$(kubectl get nodes --no-headers 2>/dev/null | wc -l)
if [ "$NODES" -gt 0 ]; then
    print_success "Found $NODES node(s)"
    kubectl get nodes
else
    print_error "No nodes found in cluster"
    exit 1
fi
echo ""

# Check namespace
print_step "Checking namespace: $NAMESPACE"
if kubectl get namespace "$NAMESPACE" &> /dev/null; then
    print_success "Namespace exists"
else
    print_error "Namespace does not exist"
    exit 1
fi
echo ""

# Check pods
print_step "Checking application pods..."
PODS=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
if [ "$PODS" -gt 0 ]; then
    print_success "Found $PODS pod(s)"
    kubectl get pods -n "$NAMESPACE"
    
    # Check pod status
    FAILED_PODS=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | grep -v "Running\|Completed" | wc -l)
    if [ "$FAILED_PODS" -gt 0 ]; then
        print_warning "Some pods are not running:"
        kubectl get pods -n "$NAMESPACE" | grep -v "Running\|Completed"
    fi
else
    print_error "No pods found in namespace"
    exit 1
fi
echo ""

# Check services
print_step "Checking services..."
SERVICES=$(kubectl get svc -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
if [ "$SERVICES" -gt 0 ]; then
    print_success "Found $SERVICES service(s)"
    kubectl get svc -n "$NAMESPACE"
else
    print_warning "No services found"
fi
echo ""

# Test health endpoint
print_step "Testing health endpoint..."
BACKEND_SVC=$(kubectl get svc -n "$NAMESPACE" -o jsonpath='{.items[?(@.metadata.name=="chatapp-backend")].metadata.name}' 2>/dev/null)

if [ -n "$BACKEND_SVC" ]; then
    print_step "Port-forwarding to backend service..."
    kubectl port-forward -n "$NAMESPACE" "svc/$BACKEND_SVC" 5000:5000 &
    PF_PID=$!
    sleep 5
    
    if curl -f http://localhost:5000/health &> /dev/null; then
        print_success "Health endpoint is responding"
        curl -s http://localhost:5000/health | head -5
    else
        print_error "Health endpoint is not responding"
        kill $PF_PID 2>/dev/null || true
        exit 1
    fi
    
    kill $PF_PID 2>/dev/null || true
else
    print_warning "Backend service not found, skipping health check"
fi
echo ""

echo "============================================================================="
print_success "Deployment validation completed!"
echo "============================================================================="
echo ""
echo "Summary:"
echo "  - Cluster: $CLUSTER_NAME"
echo "  - Namespace: $NAMESPACE"
echo "  - Nodes: $NODES"
echo "  - Pods: $PODS"
echo "  - Services: $SERVICES"
echo ""

