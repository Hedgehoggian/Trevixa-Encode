from __future__ import annotations

import itertools
import queue
import threading
from dataclasses import dataclass
from typing import Callable


@dataclass
class LocalModelSpec:
    name: str
    version: str


class LocalModelRuntime:
    """Runs up to 4 local Trevixa model workers concurrently."""

    MAX_MODELS = 4

    def __init__(self, infer_fn: Callable[[str, LocalModelSpec], str]) -> None:
        self._infer_fn = infer_fn
        self._models: list[LocalModelSpec] = [LocalModelSpec(name="Trevixa Encode Alpha", version="0.2.0")]
        self._rr = itertools.cycle(range(len(self._models)))
        self._lock = threading.RLock()
        self._models: list[LocalModelSpec] = []
        self._rr = itertools.cycle([0])
        self._lock = threading.Lock()

    def configure(self, models: list[LocalModelSpec]) -> None:
        if len(models) > self.MAX_MODELS:
            raise ValueError(f"At most {self.MAX_MODELS} local models are supported")
        if not models:
            models = [LocalModelSpec(name="Trevixa Encode Alpha", version="0.2.0")]
        with self._lock:
            self._models = models
            self._rr = itertools.cycle(range(len(models)))

    def list_models(self) -> list[LocalModelSpec]:
        with self._lock:
            return list(self._models)

    def infer(self, prompt: str) -> str:
        with self._lock:
            if not self._models:
                self.configure([])
            idx = next(self._rr)
            model = self._models[idx]
        return self._infer_fn(prompt, model)

    def infer_parallel(self, prompt: str) -> list[str]:
        models = self.list_models()
        if not models:
            self.configure([])
            models = self.list_models()

        output_queue: queue.Queue[str] = queue.Queue()
        threads: list[threading.Thread] = []

        def run_one(spec: LocalModelSpec) -> None:
            output_queue.put(self._infer_fn(prompt, spec))

        for spec in models:
            t = threading.Thread(target=run_one, args=(spec,), daemon=True)
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=30)
            t.join(timeout=20)

        outputs = []
        while not output_queue.empty():
            outputs.append(output_queue.get())
        return outputs
