#!/bin/bash

# Get the absolute directory where the script is located, and change to it.
# This makes all other paths in the script work correctly, regardless of
# where the 'claude' command was run from.
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
cd -- "$SCRIPT_DIR" || exit

# --- The rest of your script is now guaranteed to run in the right place ---

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing/updating dependencies..."
pip install fastmcp requests

# Start the MCP server
echo "Starting MCP server..."
python mcp_server.py