#!/bin/bash
set -e

# Default namespace and release name
NAMESPACE="voice-agent"
RELEASE_NAME="speech-ui"
TIMEOUT="15m0s"

echo "Deploying $RELEASE_NAME into namespace $NAMESPACE..."

# Ensure the namespace exists
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Install or upgrade the chart
# Using --atomic ensures that if the upgrade fails, it rolls back.
# Using --wait ensures it waits until all pods are ready.
# Using --timeout 15m to prevent premature failures on slow cluster/large image pulls.
helm upgrade --install $RELEASE_NAME . \
  --namespace $NAMESPACE \
  --create-namespace \
  --atomic \
  --wait \
  --timeout $TIMEOUT \
  --debug

echo "Deployment successful!"
echo "You can access the UI at: http://voice-ui.$(kubectl get svc -n istio-system istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
