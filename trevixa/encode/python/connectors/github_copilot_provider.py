from __future__ import annotations


def respond(prompt: str) -> str:
    return (
        "[GitHub Copilot connector] Direct public API access is not currently configured. "
        "Use local IDE Copilot extension auth and bridge it through MCP/tooling in a later step. "
        f"Prompt was: {prompt}"
    )
