# Trevixa Encode v0.2.0

Trevixa Encode is a hybrid **C++ + Python** app with safe/censored behavior:
- C++ launcher + bridge (`cpp/main.cpp`, `cpp/api.cpp`)
- Python CLI and GUI (`python/main.py`, `python/gui_app.py`)
- Local multi-model runtime supporting **up to 4 concurrent local models**
- Optional OpenAI/Anthropic connectors
- MCP server (`python/codex-mcp.py`)

## Quick Start

### Build C++ launcher
```bash
cmake -S trevixa/encode -B trevixa/encode/build
cmake --build trevixa/encode/build -j
```

### CLI interactive
```bash
./trevixa/encode/trevixa-encode.sh --cli
```

### CLI with 4 local models
```bash
python trevixa/encode/python/main.py --cli --chat "hello" --local-models "Trevixa-A,Trevixa-B,Trevixa-C,Trevixa-D"
python trevixa/encode/python/main.py --cli --chat "@local-all compare this" --local-models "Trevixa-A,Trevixa-B,Trevixa-C,Trevixa-D"
```

### GUI mode
```bash
./trevixa/encode/trevixa-encode.sh --gui
```

## Optional provider keys
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`

Without keys, providers run in offline mode.
