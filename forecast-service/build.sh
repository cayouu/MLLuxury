#!/bin/bash

# Script de build et push de l'image Docker

set -e

IMAGE_NAME="luxuryhouse/forecast-service"
VERSION="${1:-1.0.0}"
ACR_NAME="${ACR_NAME:-luxuryhouse.azurecr.io}"

echo "🏗️  Building Docker image..."
docker build -t $IMAGE_NAME:$VERSION -t $IMAGE_NAME:latest .

echo "🏷️  Tagging image for Azure Container Registry..."
docker tag $IMAGE_NAME:$VERSION $ACR_NAME/$IMAGE_NAME:$VERSION
docker tag $IMAGE_NAME:latest $ACR_NAME/$IMAGE_NAME:latest

echo "📤 Pushing to Azure Container Registry..."
if command -v az &> /dev/null; then
    az acr login --name ${ACR_NAME%.azurecr.io}
    docker push $ACR_NAME/$IMAGE_NAME:$VERSION
    docker push $ACR_NAME/$IMAGE_NAME:latest
    echo "✅ Image pushed: $ACR_NAME/$IMAGE_NAME:$VERSION"
else
    echo "⚠️  Azure CLI not found. Skipping push."
    echo "   Image built locally: $IMAGE_NAME:$VERSION"
fi
