#!/bin/bash
set -e

NAMESPACE="speech-diarization"
RELEASE_NAME="speech-diarization"
TIMEOUT="15m0s"

echo "Deploying ${RELEASE_NAME} to namespace ${NAMESPACE}..."

helm upgrade --install ${RELEASE_NAME} . \
    --namespace ${NAMESPACE} \
    --create-namespace \
    --atomic \
    --wait \
    --timeout ${TIMEOUT}

echo "Deployment complete."
