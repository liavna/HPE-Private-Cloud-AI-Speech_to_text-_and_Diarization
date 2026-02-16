#!/bin/bash
set -e

# Default to "latest" if no tag provided
TAG=${1:-latest}
IMAGE_NAME="liavna/speech-ui"

echo "Building Docker image: $IMAGE_NAME:$TAG"
# Build from the subdirectory where Dockerfile is located
docker build -t $IMAGE_NAME:$TAG ./docker/speech-ui

echo "Pushing Docker image: $IMAGE_NAME:$TAG"
docker push $IMAGE_NAME:$TAG

echo "Updating Helm values.yaml with tag: $TAG"
# Uses sed to replace the tag value in values.yaml at the root.
# Assumes format: tag: "something"
if [[ "$OSTYPE" == "darwin"* ]]; then
  # MacOS requires an empty string for backup extension
  sed -i '' "s/tag: \".*\"/tag: \"$TAG\"/" values.yaml
else
  sed -i "s/tag: \".*\"/tag: \"$TAG\"/" values.yaml
fi

echo "Done! Image pushed and Helm chart updated."
