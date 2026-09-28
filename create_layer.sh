#!/bin/bash
set -e

DIRECTORY="$(pwd)"
LAYER_NAME="pdf_layer"

# Remove any leftover container with the same name from previous failed runs
docker rm -f lambda-layer-container 2>/dev/null || true

# Build the Docker image
docker build -t lambda-layer "$DIRECTORY"

# Run the container (mounts host directory to /app and auto-removes container when done)
docker run --rm --name lambda-layer-container -v "$DIRECTORY:/app" lambda-layer

# Create layers directory if not created and move the zip file into it
mkdir -p "$DIRECTORY/layers"
mv "$DIRECTORY/$LAYER_NAME.zip" "$DIRECTORY/layers/$LAYER_NAME.zip"

# Cleanup: remove the Docker image
docker rmi --force lambda-layer

echo "Layer successfully created at: $DIRECTORY/layers/$LAYER_NAME.zip"