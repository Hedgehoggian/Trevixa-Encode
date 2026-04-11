#!/usr/bin/env python3
"""Minimal JSON-RPC server shim for Codex-style MCP integration."""

from __future__ import annotations

import json
import sys

from api_entrypoint import TrevixaApi

API = TrevixaApi()


def handle(req: dict) -> dict:
    method = req.get("method")
    req_id = req.get("id")

    if method == "initialize":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"name": "trevixa-encode-mcp", "version": "0.2.0"}}

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "trevixa.chat",
                        "description": "Run a safe Trevixa coding chat request",
                        "inputSchema": {"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]},
                    }
                ]
            },
        }

    if method == "tools/call":
        params = req.get("params", {})
        name = params.get("name")
        arguments = params.get("arguments", {})
        if name != "trevixa.chat":
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": f"Unknown tool: {name}"}}
        prompt = str(arguments.get("prompt", ""))
        result = API.chat_text(prompt)
        return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": result}]}}

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        req = json.loads(line)
        resp = handle(req)
        print(json.dumps(resp), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
