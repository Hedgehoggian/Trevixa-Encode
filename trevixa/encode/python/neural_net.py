from __future__ import annotations

import math
import random


class LightweightNeuralNet:
    """Tiny neural network placeholder for local scoring and experimentation."""

    def __init__(self, input_size: int, hidden_size: int, output_size: int) -> None:
        self.w1 = [[random.uniform(-0.1, 0.1) for _ in range(hidden_size)] for _ in range(input_size)]
        self.w2 = [[random.uniform(-0.1, 0.1) for _ in range(output_size)] for _ in range(hidden_size)]

    @staticmethod
    def _relu(x: float) -> float:
        return x if x > 0 else 0.0

    def forward(self, x: list[float]) -> list[float]:
        hidden = []
        for j in range(len(self.w1[0])):
            s = 0.0
            for i, v in enumerate(x[: len(self.w1)]):
                s += v * self.w1[i][j]
            hidden.append(self._relu(s))

        out = []
        for k in range(len(self.w2[0])):
            s = 0.0
            for j, h in enumerate(hidden):
                s += h * self.w2[j][k]
            out.append(1.0 / (1.0 + math.exp(-s)))
        return out
