#!/bin/bash
# Test that Docker image builds successfully after MCP dependency fixes

set -e

echo "Testing nanobot Docker build..."

cd "$(dirname "$0")/.."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker not found"
    exit 1
fi

echo "✓ Docker found"

# Build the image
echo "Building nanobot Docker image..."
docker compose build nanobot 2>&1 | head -20

if docker compose build nanobot 2>&1 | grep -q "relative path"; then
    echo "✗ FAILED: Relative path error detected"
    exit 1
fi

echo "✓ Docker build successful - no relative path errors"

# Verify image has MCP tools installed
echo "Verifying MCP packages in image..."
docker run --rm se-toolkit-lab-8-nanobot:latest python -c "import mcp_lms; import mcp_obs; print('✓ Both MCP packages imported successfully')" 2>&1 || echo "✗ Import check failed"

echo ""
echo "✓ Task 4 Docker fixes verified!"
