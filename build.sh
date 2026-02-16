#!/bin/bash
set -e

REGISTRY="liavna"
IMAGE="speech-ui"
TAG="latest"

echo "Building ${REGISTRY}/${IMAGE}:${TAG}..."

cd docker/speech-ui
docker build -t ${REGISTRY}/${IMAGE}:${TAG} .
docker push ${REGISTRY}/${IMAGE}:${TAG}
cd ../..

echo "Build and push complete."
echo "Updating values.yaml..."
# Ensure values.yaml uses 'latest' tag
sed -i 's/tag: ".*"/tag: "latest"/' values.yaml
echo "Done."
