#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import tkinter as tk
from tkinter import filedialog, ttk

from trevixa.encode.python.api_entrypoint import TrevixaApi


class TrevixaIDE:
    def __init__(self) -> None:
        self.api = TrevixaApi()
        self.root = tk.Tk()
        self.root.title("Trevixa Encode IDE v0.1.0")
        self.root.geometry("1400x800")

        self.project_dir = pathlib.Path.cwd()

        self.main = ttk.Panedwindow(self.root, orient="horizontal")
        self.main.pack(fill="both", expand=True)

        self.explorer_panel = ttk.Frame(self.main)
        self.editor_panel = ttk.Frame(self.main)
        self.chat_panel = ttk.Frame(self.main)

        self.main.add(self.explorer_panel, weight=2)
        self.main.add(self.editor_panel, weight=5)
        self.main.add(self.chat_panel, weight=3)

        self._build_explorer()
        self._build_editor()
        self._build_chat()

    def _build_explorer(self) -> None:
        top = ttk.Frame(self.explorer_panel)
        top.pack(fill="x", padx=6, pady=6)
        ttk.Button(top, text="Open Folder", command=self.open_folder).pack(side="left")
        ttk.Button(top, text="Refresh", command=self.refresh_tree).pack(side="left", padx=6)

        self.tree = ttk.Treeview(self.explorer_panel)
        self.tree.pack(fill="both", expand=True, padx=6, pady=6)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.refresh_tree()

    def _build_editor(self) -> None:
        toolbar = ttk.Frame(self.editor_panel)
        toolbar.pack(fill="x", padx=6, pady=6)
        ttk.Button(toolbar, text="Save", command=self.save_current).pack(side="left")
        ttk.Button(toolbar, text="Auto Apply", command=self.auto_apply).pack(side="left", padx=6)

        self.editor = tk.Text(self.editor_panel, wrap="none", undo=True)
        self.editor.pack(fill="both", expand=True, padx=6, pady=6)
        self.current_file: pathlib.Path | None = None

    def _build_chat(self) -> None:
        controls = ttk.Frame(self.chat_panel)
        controls.pack(fill="x", padx=6, pady=6)

        self.model_var = tk.StringVar(value="Trevixa Encode Alpha v0.2.0")
        ttk.Entry(controls, textvariable=self.model_var).pack(fill="x")

        self.chat_log = tk.Text(self.chat_panel, wrap="word", height=20)
        self.chat_log.pack(fill="both", expand=True, padx=6, pady=6)

        bottom = ttk.Frame(self.chat_panel)
        bottom.pack(fill="x", padx=6, pady=6)
        self.chat_input = ttk.Entry(bottom)
        self.chat_input.pack(side="left", fill="x", expand=True)
        self.chat_input.bind("<Return>", lambda _e: self.send_chat())
        ttk.Button(bottom, text="Send", command=self.send_chat).pack(side="left", padx=6)

    def open_folder(self) -> None:
        selected = filedialog.askdirectory(initialdir=str(self.project_dir))
        if selected:
            self.project_dir = pathlib.Path(selected)
            self.refresh_tree()

    def refresh_tree(self) -> None:
        self.tree.delete(*self.tree.get_children())
        root_item = self.tree.insert("", "end", text=str(self.project_dir), values=[str(self.project_dir)])
        for p in sorted(self.project_dir.glob("*")):
            self.tree.insert(root_item, "end", text=p.name, values=[str(p)])

    def on_tree_select(self, _event: object) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        item = selected[0]
        values = self.tree.item(item, "values")
        if not values:
            return
        p = pathlib.Path(values[0])
        if p.is_file():
            self.current_file = p
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", p.read_text(encoding="utf-8", errors="ignore"))

    def save_current(self) -> None:
        if self.current_file:
            self.current_file.write_text(self.editor.get("1.0", "end"), encoding="utf-8")

    def auto_apply(self) -> None:
        if not self.current_file:
            return
        prompt = f"Improve and clean this file: {self.current_file.name}\n\n{self.editor.get('1.0', 'end')}"
        reply = self.api.chat_text(prompt)
        self.chat_log.insert("end", f"Auto-apply suggestion:\n{reply}\n\n")

    def send_chat(self) -> None:
        prompt = self.chat_input.get().strip()
        if not prompt:
            return
        self.api.set_runtime(self.model_var.get(), "balanced", "normal")
        self.chat_log.insert("end", f"You: {prompt}\n")
        self.chat_log.insert("end", f"Trevixa: {self.api.chat_text(prompt)}\n\n")
        self.chat_input.delete(0, "end")

    def run(self) -> int:
        self.root.mainloop()
        return 0


def main() -> int:
    return TrevixaIDE().run()


if __name__ == "__main__":
    raise SystemExit(main())
