#!/bin/bash
set -e

NAMESPACE="voice-agent"
RELEASE_NAME="voice-agent"
TIMEOUT="15m0s"

echo "Deploying ${RELEASE_NAME} to namespace ${NAMESPACE}..."

helm upgrade --install ${RELEASE_NAME} . \
    --namespace ${NAMESPACE} \
    --create-namespace \
    --atomic \
    --wait \
    --timeout ${TIMEOUT}

echo "Deployment complete."
