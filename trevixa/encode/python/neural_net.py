from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
import pandas as pd

try:  # Optional acceleration/backprop engine.
    import tensorflow as tf
except Exception:  # pragma: no cover - tensorflow is optional at runtime
    tf = None


@dataclass
class TrainingConfig:
    """Configuration for local NN training."""

    learning_rate: float = 0.01
    batch_size: int = 16
    validation_split: float = 0.2
    verbose: int = 0


class LightweightNeuralNet:
    """A compact, ready-to-use neural network with NumPy + pandas helpers.

    Features:
    - Pure NumPy forward + SGD fallback (works everywhere)
    - pandas-based dataset normalization for ready-to-train workflows
    - Optional TensorFlow backend when available for stronger training dynamics
    """

    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        output_size: int,
        *,
        seed: int = 42,
        use_tensorflow: bool = False,
    ) -> None:
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.rng = np.random.default_rng(seed)

        self.w1 = self.rng.normal(0.0, 0.12, size=(input_size, hidden_size))
        self.b1 = np.zeros(hidden_size, dtype=float)
        self.w2 = self.rng.normal(0.0, 0.12, size=(hidden_size, output_size))
        self.b2 = np.zeros(output_size, dtype=float)

        self._stats: dict[str, tuple[float, float]] = {}
        self._model = None
        if use_tensorflow and tf is not None:
            self._init_tf_model()

    @staticmethod
    def _relu(x: np.ndarray) -> np.ndarray:
        return np.maximum(x, 0.0)

    @staticmethod
    def _relu_grad(x: np.ndarray) -> np.ndarray:
        return (x > 0).astype(float)

    @staticmethod
    def _sigmoid(x: np.ndarray) -> np.ndarray:
        clipped = np.clip(x, -60.0, 60.0)
        return 1.0 / (1.0 + np.exp(-clipped))

    def _init_tf_model(self) -> None:
        if tf is None:
            return
        model = tf.keras.Sequential(
            [
                tf.keras.layers.Input(shape=(self.input_size,)),
                tf.keras.layers.Dense(self.hidden_size, activation="relu"),
                tf.keras.layers.Dense(self.output_size, activation="sigmoid"),
            ]
        )
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), loss="mse")
        self._model = model

    def _ensure_vector(self, x: Sequence[float]) -> np.ndarray:
        vector = np.asarray(list(x), dtype=float)
        if vector.shape[0] < self.input_size:
            vector = np.pad(vector, (0, self.input_size - vector.shape[0]))
        elif vector.shape[0] > self.input_size:
            vector = vector[: self.input_size]
        return vector

    def forward(self, x: Sequence[float]) -> list[float]:
        """Inference entrypoint compatible with existing call sites."""
        vector = self._ensure_vector(x)

        if self._model is not None:
            out = self._model(vector.reshape(1, -1), training=False).numpy()[0]
            return out.astype(float).tolist()

        z1 = vector @ self.w1 + self.b1
        h = self._relu(z1)
        z2 = h @ self.w2 + self.b2
        out = self._sigmoid(z2)
        return out.astype(float).tolist()

    def _to_feature_frame(self, samples: Iterable[Sequence[float]]) -> pd.DataFrame:
        frame = pd.DataFrame(samples)
        if frame.empty:
            return pd.DataFrame(columns=[f"f{i}" for i in range(self.input_size)])

        frame = frame.fillna(0.0)
        if frame.shape[1] < self.input_size:
            for i in range(frame.shape[1], self.input_size):
                frame[i] = 0.0
        frame = frame.iloc[:, : self.input_size]
        frame.columns = [f"f{i}" for i in range(self.input_size)]

        for col in frame.columns:
            mu = float(frame[col].mean())
            sigma = float(frame[col].std(ddof=0))
            sigma = sigma if sigma > 1e-8 else 1.0
            self._stats[col] = (mu, sigma)
            frame[col] = (frame[col] - mu) / sigma
        return frame

    def _normalize_with_existing_stats(self, frame: pd.DataFrame) -> pd.DataFrame:
        aligned = frame.copy()
        for col in aligned.columns:
            mu, sigma = self._stats.get(col, (0.0, 1.0))
            aligned[col] = (aligned[col] - mu) / sigma
        return aligned

    def fit(
        self,
        inputs: Iterable[Sequence[float]],
        targets: Iterable[Sequence[float]],
        epochs: int = 10,
        config: TrainingConfig | None = None,
    ) -> dict[str, float]:
        """Train the model on batch data.

        Uses TensorFlow if enabled; otherwise falls back to NumPy SGD.
        """
        cfg = config or TrainingConfig()
        x_df = self._to_feature_frame(inputs)
        y = np.asarray(list(targets), dtype=float)

        if x_df.empty or y.size == 0:
            return {"loss": 0.0, "samples": 0}

        x = x_df.to_numpy(dtype=float)
        if y.ndim == 1:
            y = y.reshape(-1, 1)
        if y.shape[1] < self.output_size:
            y = np.pad(y, ((0, 0), (0, self.output_size - y.shape[1])))
        elif y.shape[1] > self.output_size:
            y = y[:, : self.output_size]

        if self._model is not None:
            hist = self._model.fit(
                x,
                y,
                epochs=max(1, epochs),
                batch_size=max(1, cfg.batch_size),
                validation_split=max(0.0, min(0.9, cfg.validation_split)),
                verbose=cfg.verbose,
            )
            loss = float(hist.history["loss"][-1])
            return {"loss": loss, "samples": float(len(x))}

        lr = max(1e-5, cfg.learning_rate)
        batch = max(1, cfg.batch_size)
        last_loss = math.inf
        for _ in range(max(1, epochs)):
            order = self.rng.permutation(len(x))
            for start in range(0, len(x), batch):
                idx = order[start : start + batch]
                xb = x[idx]
                yb = y[idx]

                z1 = xb @ self.w1 + self.b1
                h = self._relu(z1)
                z2 = h @ self.w2 + self.b2
                pred = self._sigmoid(z2)

                err = pred - yb
                last_loss = float(np.mean(err**2))

                d_out = 2.0 * err * pred * (1.0 - pred)
                grad_w2 = h.T @ d_out / len(xb)
                grad_b2 = np.mean(d_out, axis=0)

                d_hidden = (d_out @ self.w2.T) * self._relu_grad(z1)
                grad_w1 = xb.T @ d_hidden / len(xb)
                grad_b1 = np.mean(d_hidden, axis=0)

                self.w2 -= lr * grad_w2
                self.b2 -= lr * grad_b2
                self.w1 -= lr * grad_w1
                self.b1 -= lr * grad_b1

        return {"loss": float(last_loss), "samples": float(len(x))}

    def predict_batch(self, inputs: Iterable[Sequence[float]]) -> list[list[float]]:
        frame = pd.DataFrame(inputs).fillna(0.0)
        if frame.empty:
            return []
        if frame.shape[1] < self.input_size:
            for i in range(frame.shape[1], self.input_size):
                frame[i] = 0.0
        frame = frame.iloc[:, : self.input_size]
        frame.columns = [f"f{i}" for i in range(self.input_size)]
        if self._stats:
            frame = self._normalize_with_existing_stats(frame)

        if self._model is not None:
            out = self._model(frame.to_numpy(dtype=float), training=False).numpy()
            return out.astype(float).tolist()

        x = frame.to_numpy(dtype=float)
        hidden = self._relu(x @ self.w1 + self.b1)
        out = self._sigmoid(hidden @ self.w2 + self.b2)
        return out.astype(float).tolist()
