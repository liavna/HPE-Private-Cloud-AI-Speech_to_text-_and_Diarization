#!/bin/bash
set -e

NAMESPACE="speech-diarization"
RELEASE_NAME="speech-diarization"
CHART_NAME="speech-diarization-ui"
VERSION="1.0.0"
TIMEOUT="15m0s"

echo "Packaging ${CHART_NAME} version ${VERSION}..."
helm package .

echo "Deploying ${RELEASE_NAME} to namespace ${NAMESPACE}..."

helm upgrade --install ${RELEASE_NAME} ${CHART_NAME}-${VERSION}.tgz \
    --namespace ${NAMESPACE} \
    --create-namespace \
    --atomic \
    --wait \
    --timeout ${TIMEOUT}

echo "Deployment complete."
