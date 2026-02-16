#!/bin/bash
set -e

# Default variables
IMAGE_NAME="liavna/speech-ui"
TAG=$(git describe --tags --always --dirty 2>/dev/null || echo "latest")

# Allow overriding TAG
if [ -n "$1" ]; then
    TAG="$1"
fi

echo "Building Docker image: $IMAGE_NAME:$TAG"

# Build the image from the docker/speech-ui context
docker build -t "$IMAGE_NAME:$TAG" -f docker/speech-ui/Dockerfile docker/speech-ui

echo "Pushing Docker image: $IMAGE_NAME:$TAG"
docker push "$IMAGE_NAME:$TAG"

# Also push as latest if it's not already
if [ "$TAG" != "latest" ]; then
    echo "Tagging and pushing as latest..."
    docker tag "$IMAGE_NAME:$TAG" "$IMAGE_NAME:latest"
    docker push "$IMAGE_NAME:latest"
fi

echo "Build and push complete!"
