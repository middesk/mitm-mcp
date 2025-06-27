from fastmcp import FastMCP
import json
import os
import glob
from datetime import datetime
from urllib.parse import urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import base64

# --- Main MCP Application ---
mcp = FastMCP("Mitmproxy MCP Server")

# Create flows directory if it doesn't exist
FLOWS_DIR = "flows"
os.makedirs(FLOWS_DIR, exist_ok=True)

def decode_flow(data):
    """Recursively decodes base64 strings in a dictionary."""
    if isinstance(data, dict):
        return {k: decode_flow(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [decode_flow(i) for i in data]
    elif isinstance(data, str):
        try:
            return base64.b64decode(data).decode('utf-8')
        except (ValueError, TypeError):
            return data
    else:
        return data

def generate_filename(flow_data: dict) -> str:
    """Generate a filename for the flow based on timestamp, method, and URL."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    method = flow_data.get("request", {}).get("method", "UNKNOWN")
    
    # Try to get path from either url or path field
    url_part = "unknown"
    request = flow_data.get("request", {})
    
    if "url" in request and request["url"]:
        # Direct URL (like test flows)
        parsed_url = urlparse(request["url"])
        url_part = f"{parsed_url.netloc}{parsed_url.path}".replace("/", "-").replace(":", "_")
    elif "path" in request and request["path"]:
        # Path field from mitmproxy flows
        path = request["path"]
        # Clean up the path to be more readable
        url_part = path.strip("/").replace("/", "-")
    
    flow_id = flow_data.get("id", "")[:8]
    
    # Clean up parts for filename
    method = method.upper()
    url_part = "".join(c for c in url_part if c.isalnum() or c in "-_").strip("-_")
    if len(url_part) > 50:
        url_part = url_part[:50]
        
    return f"{timestamp}_{method}_{url_part}_{flow_id}.json"

@mcp.tool()
def list_flows():
    """Lists all available flow files."""
    flow_files = sorted(glob.glob(os.path.join(FLOWS_DIR, "*.json")), reverse=True)
    return {
        "flow_files": [os.path.basename(f) for f in flow_files],
        "count": len(flow_files)
    }

@mcp.tool()
def clear_flows():
    """Clears all captured mitmproxy flows."""
    deleted_count = 0
    for file_path in glob.glob(os.path.join(FLOWS_DIR, "*.json")):
        try:
            os.remove(file_path)
            deleted_count += 1
        except OSError as e:
            print(f"Error deleting {file_path}: {e}")
            
    return {"status": "cleared", "deleted_files": deleted_count}

@mcp.tool()
def read_flow(filename: str):
    """Reads a specific flow file and returns its contents."""
    file_path = os.path.join(FLOWS_DIR, filename)
    if not os.path.exists(file_path):
        return {"error": f"Flow file '{filename}' not found"}
        
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        return {"error": f"Error reading flow file: {e}"}

# --- Internal Flow Handling Logic ---
def add_flow(flow_data: dict):
    """
    Saves a mitmproxy flow to a file. This is an internal function and not an MCP tool.
    """
    try:
        decoded_flow = decode_flow(flow_data)
        filename = generate_filename(decoded_flow)
        file_path = os.path.join(FLOWS_DIR, filename)
        
        with open(file_path, 'w') as f:
            json.dump(decoded_flow, f, indent=2)
            
        return {"status": "ok", "filename": filename}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# --- Custom HTTP Server for Receiving Flows ---
class FlowSubmitHandler(BaseHTTPRequestHandler):
    """A simple handler for receiving flow data via POST requests."""
    def do_POST(self):
        if self.path == '/submit_flow':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                flow_data = json.loads(post_data)
                
                result = add_flow(flow_data)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
        else:
            self.send_error(404, "Not Found")

    def log_message(self, format, *args):
        """Suppresses log messages to keep the console clean."""
        return

def run_flow_submit_server(host='127.0.0.1', port=8124):
    """Runs the flow submission HTTP server."""
    server_address = (host, port)
    with HTTPServer(server_address, FlowSubmitHandler) as httpd:
        print(f"Internal flow submission server listening on http://{host}:{port}")
        httpd.serve_forever()

# --- Main Execution ---
if __name__ == "__main__":
    submit_server_thread = threading.Thread(target=run_flow_submit_server, daemon=True)
    submit_server_thread.start()
    
    print("Starting main MCP Server on port 8124...")
    mcp.run()