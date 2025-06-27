# write_to_mcp.py
import requests
import json
import logging
import base64

# Setup basic logging to see output from the mitmproxy script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - mitmproxy - %(message)s')

# The URL for the new custom flow submission server
SUBMIT_SERVER_URL = "http://127.0.0.1:8124/submit_flow"

def serialize_bytes(obj):
    """Recursively convert bytes objects to base64 strings for JSON serialization."""
    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')
    elif isinstance(obj, dict):
        return {key: serialize_bytes(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_bytes(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(serialize_bytes(item) for item in obj)
    else:
        return obj

def send_flow_to_server(flow_state: dict):
    """Sends a flow's state to the custom submission server."""
    try:
        # Convert bytes objects to base64 strings for JSON serialization
        serializable_flow_state = serialize_bytes(flow_state)
        response = requests.post(SUBMIT_SERVER_URL, json=serializable_flow_state, timeout=5)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        # We log the success but don't need to print the full response to keep logs tidy.
        logging.info(f"Successfully sent flow to internal server.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send flow to server: {e}")

def response(flow):
    """Mitmproxy event handler called for each server response."""
    # flow.get_state() returns a JSON-serializable representation of the flow
    flow_state = flow.get_state()
    send_flow_to_server(flow_state)