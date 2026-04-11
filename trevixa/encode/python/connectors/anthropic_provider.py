from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


def respond(prompt: str, model: str = "claude-3-5-sonnet-latest") -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return f"[Anthropic offline stub] Set ANTHROPIC_API_KEY to enable live calls. Prompt: {prompt}"

    url = "https://api.anthropic.com/v1/messages"
    payload = {
        "model": model,
        "max_tokens": 800,
        "messages": [{"role": "user", "content": prompt}],
        "system": "You are a helpful, safety-focused coding assistant.",
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            blocks = body.get("content", [])
            if blocks and isinstance(blocks, list):
                return "".join(block.get("text", "") for block in blocks).strip()
            return json.dumps(body)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")
        return f"[Anthropic error] HTTP {e.code}: {detail}"
    except Exception as e:  # noqa: BLE001
        return f"[Anthropic error] {e}"
