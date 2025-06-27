#!/bin/bash
mitmproxy --mode reverse:http://127.0.0.1:3123 -p 3002 -s ./write_to_mcp.py