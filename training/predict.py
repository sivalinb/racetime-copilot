"""Inference-only demo for the merged local router; no training or file writes."""

import time
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LABELS = ["recap", "runner", "verify", "compare"]


@lru_cache(maxsize=1)
def load_model():
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    if not (ROOT / "merged" / "config.json").exists():
        raise ValueError("Run training/train_router.py and training/infer.py first.")
    return (
        AutoTokenizer.from_pretrained(ROOT / "merged", local_files_only=True),
        AutoModelForSequenceClassification.from_pretrained(
            ROOT / "merged", local_files_only=True
        ).eval(),
    )


def predict(question):
    import torch

    if not question.strip() or len(question) > 1000:
        raise ValueError("Enter a question between 1 and 1000 characters.")
    tokenizer, model = load_model()
    started = time.monotonic()
    with torch.no_grad():
        probabilities = model(
            **tokenizer(question, return_tensors="pt", truncation=True, max_length=64)
        ).logits.softmax(-1)[0]
    return {
        "question": question,
        "route": LABELS[int(probabilities.argmax())],
        "softmax_score": float(probabilities.max()),
        "warm_inference_ms": round((time.monotonic() - started) * 1000, 2),
        "note": "Uncalibrated classifier score. Separate lab; does not control the production video agent.",
    }
