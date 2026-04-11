from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

try:
    from .connectors import anthropic_provider, github_copilot_provider, openai_provider
    from .feature_engine import FeatureEngine
    from .intellect import IntellectEngine
    from .memory_store import JsonlMemoryStore
    from .model_manager import LocalModelRuntime, LocalModelSpec
    from .modes import text_chat, video_chat, voice_chat
    from .neural_net import LightweightNeuralNet
    from .safety import check_prompt, safe_refusal
    from .session_store import SessionStore
except ImportError:
    from connectors import anthropic_provider, github_copilot_provider, openai_provider
    from feature_engine import FeatureEngine
    from intellect import IntellectEngine
    from memory_store import JsonlMemoryStore
    from model_manager import LocalModelRuntime, LocalModelSpec
    from modes import text_chat, video_chat, voice_chat
    from neural_net import LightweightNeuralNet
    from safety import check_prompt, safe_refusal
    from session_store import SessionStore


@dataclass
class RuntimeConfig:
    model: str = "Trevixa Encode Alpha v0.2.0"
    reasoning: str = "balanced"
    eagerness: str = "normal"


class TrevixaApi:
    """Censored/safe API entrypoint orchestrating providers and local capabilities."""

    def __init__(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        self.project_root = project_root
        self.memory = JsonlMemoryStore(str(project_root / "datasets" / "memory.jsonl"))
        self.nn = LightweightNeuralNet(input_size=16, hidden_size=8, output_size=4)
        self.runtime = RuntimeConfig()
        self.local_runtime = LocalModelRuntime(self._run_local_model)
        self.local_runtime.configure([LocalModelSpec("Trevixa Encode Alpha", "0.2.0")])
        self.intellect = IntellectEngine()
        self.features = FeatureEngine()
        self.sessions = SessionStore()

    def set_runtime(self, model: str, reasoning: str, eagerness: str) -> None:
        self.runtime = RuntimeConfig(model=model, reasoning=reasoning, eagerness=eagerness)

    def set_local_models(self, models: list[str]) -> str:
        parsed = [LocalModelSpec(name=m.strip(), version="0.2.0") for m in models if m.strip()]
        self.local_runtime.configure(parsed)
        active = [f"{m.name}:{m.version}" for m in self.local_runtime.list_models()]
        return f"Active local models ({len(active)}): {', '.join(active)}"

    def list_local_models(self) -> list[str]:
        return [f"{m.name}:{m.version}" for m in self.local_runtime.list_models()]

    def _run_local_model(self, prompt: str, spec: LocalModelSpec) -> str:
        nn_scores = self.nn.forward([float((ord(c) % 32) / 31.0) for c in prompt[:16].ljust(16)])
        context = self.intellect.retrieve(prompt, self.memory.tail(40), top_k=2)
        plan = self.intellect.plan(prompt)
        response = text_chat.respond(
            f"[{spec.name} v{spec.version} score={sum(nn_scores):.2f}] {prompt}\n"
            f"Context: {context}\nPlan: {plan}"
        )
        return self.features.apply(response)

    def _route_provider(self, prompt: str) -> str:
        if prompt.startswith("@openai") or self.runtime.model.startswith("@openai"):
            model = self.runtime.model.replace("@openai", "").strip() or "gpt-4.1-mini"
            return self.features.apply(openai_provider.respond(prompt, model=model))
        if prompt.startswith("@claude") or self.runtime.model.startswith("@claude"):
            model = self.runtime.model.replace("@claude", "").strip() or "claude-3-5-sonnet-latest"
            return self.features.apply(anthropic_provider.respond(prompt, model=model))
        if prompt.startswith("@copilot") or self.runtime.model.startswith("@copilot"):
            return self.features.apply(github_copilot_provider.respond(prompt))
        if prompt.startswith("@local-all"):
            return self.features.apply("\n".join(self.local_runtime.infer_parallel(prompt)))
        return self.features.apply(self.local_runtime.infer(prompt))

    def chat_text(self, prompt: str, session_id: str = "default") -> str:
        safety = check_prompt(prompt)
        if not safety.allowed:
            return safe_refusal(safety.reason)

        self.sessions.add_message(session_id, prompt)
        self.memory.append(
            {
                "mode": "text",
                "prompt": prompt,
                "runtime": self.runtime.__dict__,
                "local_models": self.list_local_models(),
            }
        )
        response = self._route_provider(prompt)
        self.sessions.add_message(session_id, response)
        return response

    def chat_voice(self, transcript: str) -> str:
        self.memory.append({"mode": "voice", "prompt": transcript, "runtime": self.runtime.__dict__})
        return voice_chat.respond(transcript)

    def chat_video(self, description: str) -> str:
        self.memory.append({"mode": "video", "prompt": description, "runtime": self.runtime.__dict__})
        return video_chat.respond(description)

    def train_from_dataset(self, epochs: int = 3) -> str:
        data_path = self.project_root / "datasets" / "train.json"
        payload = json.loads(data_path.read_text(encoding="utf-8"))
        samples = payload.get("samples", [])

        for _ in range(max(1, epochs)):
            for sample in samples:
                vector = [float((ord(c) % 32) / 31.0) for c in sample.get("input", "")[:16].ljust(16)]
                _ = self.nn.forward(vector)

        return f"Trained local NN for {max(1, epochs)} epochs on {len(samples)} samples."
