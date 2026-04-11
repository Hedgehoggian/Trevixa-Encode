from __future__ import annotations

import tkinter as tk
from tkinter import ttk

try:
    from .api_entrypoint import TrevixaApi
except ImportError:
    from api_entrypoint import TrevixaApi
from api_entrypoint import TrevixaApi


def launch_gui() -> int:
    api = TrevixaApi()

    root = tk.Tk()
    root.title("Trevixa Encode v0.2.0")
    root.geometry("980x640")

    model_var = tk.StringVar(value="Trevixa Encode Alpha v0.2.0")
    reason_var = tk.StringVar(value="balanced")
    eager_var = tk.StringVar(value="normal")
    local_models_var = tk.StringVar(value="Trevixa-Local-A,Trevixa-Local-B")

    top = ttk.Frame(root, padding=8)
    top.pack(fill="x")

    ttk.Label(top, text="Model").grid(row=0, column=0, sticky="w")
    ttk.Combobox(top, textvariable=model_var, values=[
        "Trevixa Encode Alpha v0.2.0",
        "Trevixa Latest Stable Release",
        "Trevixa v1.0.0",
        "@openai gpt-4.1-mini",
        "@claude claude-3-5-sonnet-latest",
    ], width=35).grid(row=0, column=1, padx=6)

    ttk.Label(top, text="Reasoning").grid(row=0, column=2, sticky="w")
    ttk.Combobox(top, textvariable=reason_var, values=["light", "balanced", "deep"], width=12).grid(row=0, column=3, padx=6)

    ttk.Label(top, text="Eagerness").grid(row=0, column=4, sticky="w")
    ttk.Combobox(top, textvariable=eager_var, values=["careful", "normal", "proactive"], width=12).grid(row=0, column=5, padx=6)

    ttk.Label(top, text="Local Models (max 4)").grid(row=1, column=0, sticky="w")
    ttk.Entry(top, textvariable=local_models_var, width=50).grid(row=1, column=1, columnspan=3, sticky="we", padx=6)

    transcript = tk.Text(root, wrap="word")
    transcript.pack(fill="both", expand=True, padx=8, pady=8)

    input_frame = ttk.Frame(root, padding=8)
    input_frame.pack(fill="x")
    prompt_entry = ttk.Entry(input_frame)
    prompt_entry.pack(side="left", fill="x", expand=True)

    def sync_runtime() -> None:
        names = [n.strip() for n in local_models_var.get().split(",") if n.strip()]
        api.set_local_models(names)
        api.set_runtime(model=model_var.get(), reasoning=reason_var.get(), eagerness=eager_var.get())

    def send() -> None:
        prompt = prompt_entry.get().strip()
        if not prompt:
            return
        sync_runtime()
        transcript.insert("end", f"You: {prompt}\n")
        transcript.insert("end", f"Trevixa: {api.chat_text(prompt)}\n\n")
        transcript.see("end")
        prompt_entry.delete(0, "end")

    ttk.Button(input_frame, text="Send", command=send).pack(side="left", padx=8)
    prompt_entry.bind("<Return>", lambda _event: send())

    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(launch_gui())
