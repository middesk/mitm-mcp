.PHONY: all mcp mitm setup help

# Default target
all: help

# Ensure scripts are executable
setup:
	@chmod +x start-mcp.sh start-mitm.sh

# Start the MCP server
mcp: setup
	@echo "Starting MCP server..."
	./start-mcp.sh

# Start the MITM proxy
mitm: setup
	@echo "Starting MITM proxy..."
	./start-mitm.sh

# Help target
help:
	@echo "Available targets:"
	@echo "  make mcp   - Start the MCP server"
	@echo "  make mitm  - Start the MITM proxy"
	@echo "  make setup - Ensure scripts are executable"
	@echo "  make help  - Show this help message" 