#!/bin/bash
# Script to build and push Docker image to registry

set -e

# Configuration
REGISTRY="${1:-your-registry}"
IMAGE_NAME="youtube-sentiment-analysis"
VERSION="${2:-latest}"
FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${VERSION}"

echo "🚀 Building Docker image: ${FULL_IMAGE_NAME}"

# Build the image
docker build -t "${FULL_IMAGE_NAME}" .

echo "✅ Build complete!"
echo ""
echo "📦 To test locally, run:"
echo "   docker run -d --name youtube-sentiment-test -p 8501:8501 -e YOUTUBE_API_KEY=your_key ${FULL_IMAGE_NAME}"
echo ""
read -p "Push to registry? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "📤 Pushing to registry..."
    docker push "${FULL_IMAGE_NAME}"
    echo "✅ Push complete!"
    echo ""
    echo "🎉 Image available at: ${FULL_IMAGE_NAME}"
    echo ""
    echo "For your friend to run:"
    echo "   docker pull ${FULL_IMAGE_NAME}"
    echo "   docker run -d --name youtube-sentiment -p 8501:8501 -e YOUTUBE_API_KEY=their_key ${FULL_IMAGE_NAME}"
fi
