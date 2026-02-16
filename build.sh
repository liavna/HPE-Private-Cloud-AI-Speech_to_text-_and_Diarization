#!/bin/bash
REPO="liavna"
APP="speech.ai"
TAG="latest"

echo "🛠️ Building $REPO/$APP:$TAG..."
docker build -t $REPO/$APP:$TAG ./docker/speech-ui
echo "🚀 Pushing to $REPO..."
docker push $REPO/$APP:$TAG
echo "✅ Done!"
