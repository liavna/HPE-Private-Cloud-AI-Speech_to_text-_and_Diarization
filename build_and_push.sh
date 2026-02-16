#!/bin/bash
set -e

# Default to "latest" if no tag provided
TAG=${1:-latest}
IMAGE_NAME="liavna/speech-ui"

echo "Building Docker image: $IMAGE_NAME:$TAG"
docker build -t $IMAGE_NAME:$TAG .

echo "Pushing Docker image: $IMAGE_NAME:$TAG"
docker push $IMAGE_NAME:$TAG

echo "Updating Helm values.yaml with tag: $TAG"
# Uses sed to replace the tag value in values.yaml.
# Assumes format: tag: "something"
if [[ "$OSTYPE" == "darwin"* ]]; then
  # MacOS requires an empty string for backup extension
  sed -i '' "s/tag: \".*\"/tag: \"$TAG\"/" charts/speech-ui/values.yaml
else
  sed -i "s/tag: \".*\"/tag: \"$TAG\"/" charts/speech-ui/values.yaml
fi

echo "Done! Image pushed and Helm chart updated."
