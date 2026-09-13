"""Export the measured per-step loss curves; no smoothed or invented points."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
report = json.loads((ROOT / "reports/router-evaluation.json").read_text())
fig, ax = plt.subplots(figsize=(10, 5), layout="constrained")
for name, color in [("frozen_encoder", "#64748b"), ("lora", "#0891b2")]:
    loss = report["results"][name]["loss_by_step"]
    ax.plot(
        range(1, len(loss) + 1), loss, label=name.replace("_", " ").title(), color=color
    )
ax.set(
    title="RaceTime LoRA training: actual loss at every update",
    xlabel="Optimizer update",
    ylabel="Training loss",
)
ax.legend()
ax.grid(alpha=0.2)
fig.savefig(ROOT / "reports/week5-training-curve.png", dpi=160)
