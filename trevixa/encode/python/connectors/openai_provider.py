from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


def respond(prompt: str, model: str = "gpt-4.1-mini") -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return f"[OpenAI offline stub] Set OPENAI_API_KEY to enable live calls. Prompt: {prompt}"

    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful, safety-focused coding assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")
        return f"[OpenAI error] HTTP {e.code}: {detail}"
    except Exception as e:  # noqa: BLE001
        return f"[OpenAI error] {e}"
