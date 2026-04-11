# Trevixa Encode v0.2.0

Trevixa Encode is a hybrid **C++ + Python** app with safe/censored behavior.

## Highlights
- C++ launcher + Python bridge
- CLI and GUI
- Up to 4 local models running concurrently
- Intellect engine (retrieval + plan synthesis)
- 500+ implemented micro-features enabled through FeatureEngine
- MCP server
- Optional OpenAI / Anthropic live provider support

## Quick Start

```bash
cmake -S trevixa/encode -B trevixa/encode/build
cmake --build trevixa/encode/build -j
```

CLI:
```bash
./trevixa/encode/trevixa-encode.sh --cli
python trevixa/encode/python/main.py --cli --chat "@local-all compare" --local-models "A,B,C,D"
```

GUI:
```bash
./trevixa/encode/trevixa-encode.sh --gui
```

VS Code extension moved to:
- `trevixa/vscext`

IDE app:
- `trevixa/devenv/python/ide_main.py`
