# Mitm-mcp
This repository implements an MCP for mitmproxy. [Mitmproxy](https://github.com/mitmproxy/mitmproxy) is a very popular tool to inspect network requests via a proxy.
<img width="400" alt="Screenshot 2025-06-27 at 1 31 07 PM" src="https://github.com/user-attachments/assets/0d6434b0-5dc5-4d4d-8308-4b7b5b3438ea" />

We can extend mitmproxy with an MCP to do things like:
```
> Can you see the most recent flow that I've sent?
  ⎿ {
      "flow_files": [
        "2025-06-27_12-41-14_GET_v1-agent-companiessort_bycreated_atsort_or
    … +157 lines (ctrl+r to expand)


⏺ mitm-proxy:read_flow (MCP)(filename:
                            "2025-06-27_12-41-14_GET_v1-agent-companiessort_b
                            ycreated_atsort_orderasc_7680c941.json")
  ⎿  {
       "version": 21,
       "type": "http",
     … +346 lines (ctrl+r to expand)

⏺ The most recent flow shows a successful GET request to
  /v1/agent/companies?sort_by=created_at&sort_order=asc. This request
  returned a list of companies with detailed information about "Middesk
  Inc.", including its owners, individuals, addresses, and tax agency
  registrations. The request was authenticated with a Bearer token and
  returned a 200 OK status.
```
## Setup
We need to start mitmproxy and the mcp server. Mitmproxy pushes messages to the mcp server via a python script.

Here's how to get started:
```
// Start service on alternate port, for example we use 3123 instead of regular 3002.
bundle exec rails s -p 3123

// Start mitmproxy and mcp server
make mitm
make mcp

// Add MCP to your LLM, for claude code it is:
claude mcp add --scope user mitm-proxy -- [YOUR-WORKSPACE]/mitm-mcp/start-mcp.sh
```

Now restart your LLM and you should see the tool calls:
* `list_flows`
* `clear_flows`
* `read_flow`
