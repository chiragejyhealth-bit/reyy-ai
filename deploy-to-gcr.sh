#!/bin/bash
set -e

# Configuration
PROJECT_ID="future-function-466418-i7"
REGION="us-central1"
REPOSITORY="reyy-ai"
IMAGE_NAME="reyy-ai"
IMAGE_TAG=$(date +%Y%m%d-%H%M%S)

# Full image path
FULL_IMAGE_PATH="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"
LATEST_IMAGE_PATH="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:latest"

echo "Building Docker image..."
docker build -t ${FULL_IMAGE_PATH} .
docker tag ${FULL_IMAGE_PATH} ${LATEST_IMAGE_PATH}

echo "Authenticating with Google Cloud..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

echo "Pushing image to Artifact Registry..."
docker push ${FULL_IMAGE_PATH}
docker push ${LATEST_IMAGE_PATH}

echo "Image pushed successfully to: ${FULL_IMAGE_PATH}"
echo "Also tagged as latest: ${LATEST_IMAGE_PATH}" 