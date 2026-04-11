#!/usr/bin/env python3
"""Trevixa Encode CLI + C++ bridge target."""

from __future__ import annotations

import argparse
import json
from typing import Callable

try:
    from .api_entrypoint import TrevixaApi
    from .gui_app import launch_gui
except ImportError:
    from api_entrypoint import TrevixaApi
    from gui_app import launch_gui
from api_entrypoint import TrevixaApi
from gui_app import launch_gui


def cli_banner() -> str:
    return (
        "Trevixa Encode CLI ready.\n"
        "Commands: /model NAME, /reason VALUE, /eager VALUE, /local NAME1,NAME2,NAME3,NAME4, /local-list, /history, /quit\n"
        "Commands: /model NAME, /reason VALUE, /eager VALUE, /local NAME1,NAME2,NAME3,NAME4, /local-list, /quit\n"
    )


def health_check() -> str:
    return json.dumps({"status": "ok", "service": "trevixa-encode", "version": "0.2.0"})


def gui_state(raw: str = "") -> str:
    return json.dumps({"gui": "connected", "state": raw})


def launch_gui_bridge() -> str:
    launch_gui()
    return json.dumps({"gui": "closed"})


BRIDGE_FUNCTIONS: dict[str, Callable[..., str]] = {
    "cli_banner": cli_banner,
    "health_check": health_check,
    "gui_state": gui_state,
    "launch_gui": launch_gui_bridge,
}


def parse_runtime_command(api: TrevixaApi, raw: str) -> bool:
    if raw.startswith("/model "):
        api.runtime.model = raw.split(" ", 1)[1].strip()
        print(f"Model set to {api.runtime.model}")
        return True
    if raw.startswith("/reason "):
        api.runtime.reasoning = raw.split(" ", 1)[1].strip()
        print(f"Reasoning set to {api.runtime.reasoning}")
        return True
    if raw.startswith("/eager "):
        api.runtime.eagerness = raw.split(" ", 1)[1].strip()
        print(f"Eagerness set to {api.runtime.eagerness}")
        return True
    if raw.startswith("/local "):
        names = [n.strip() for n in raw.split(" ", 1)[1].split(",")]
        print(api.set_local_models(names))
        return True
    if raw == "/local-list":
        print("\n".join(api.list_local_models()))
        return True
    if raw == "/history":
        print("\n".join(api.sessions.history("default")))
        return True
    return False


def run_cli(chat_text: str | None, interactive: bool, local_models: str | None) -> int:
    api = TrevixaApi()
    if local_models:
        names = [n.strip() for n in local_models.split(",")]
        api.set_local_models(names)

    print(cli_banner(), end="")

    if chat_text:
        print(api.chat_text(chat_text))

    if interactive:
        while True:
            raw = input("trevixa> ").strip()
            if not raw:
                continue
            if raw in {"/quit", "/exit"}:
                break
            if parse_runtime_command(api, raw):
                continue
            print(api.chat_text(raw))

    return 0


def run_bridge(function_name: str, args: list[str]) -> int:
    fn = BRIDGE_FUNCTIONS.get(function_name)
    if not fn:
        print(json.dumps({"error": f"unknown bridge function: {function_name}"}))
        return 1
    print(fn(*args), end="")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Trevixa Encode Python CLI")
    parser.add_argument("--cli", action="store_true")
    parser.add_argument("--bridge", nargs="+")
    parser.add_argument("--chat", type=str)
    parser.add_argument("--interactive", action="store_true")
    parser.add_argument("--train", action="store_true")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--local-models", type=str, help="Comma-separated local model names (max 4)")
    args = parser.parse_args()

    if args.bridge:
        return run_bridge(args.bridge[0], args.bridge[1:])

    if args.train:
        print(TrevixaApi().train_from_dataset(epochs=args.epochs))
        return 0

    return run_cli(args.chat, args.interactive, args.local_models)


if __name__ == "__main__":
    raise SystemExit(main())
