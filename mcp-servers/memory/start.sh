#!/bin/bash
# Memory Server Startup Script

cd "$(dirname "$0")"

# Ensure the server is built
npm run build

# Set the memory file path
export MEMORY_FILE="$(pwd)/memory.json"

# Start the memory server
echo "Starting Memory Server..."
echo "Memory file: $MEMORY_FILE"
node dist/index.js