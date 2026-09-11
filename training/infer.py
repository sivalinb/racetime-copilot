"""Smoke-test adapter merge and run the local intent classifier."""

import json
import sys
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoTokenizer, BertConfig, BertForSequenceClassification

ROOT = Path(__file__).resolve().parent
report = json.loads((ROOT.parent / "reports/router-evaluation.json").read_text())
base = BertForSequenceClassification.from_pretrained(
    report["model"],
    config=BertConfig.from_pretrained(
        report["model"], num_labels=4, cache_dir=ROOT / "cache"
    ),
    cache_dir=ROOT / "cache",
)
model = PeftModel.from_pretrained(base, ROOT / "checkpoints/adapter").eval()
tok = AutoTokenizer.from_pretrained(ROOT / "checkpoints/adapter")
questions = [
    "Recap the last part of the broadcast.",
    "Compare those two race sections.",
    "Verify whether the graphic contradicts the commentary.",
    "Any news about bib 42?",
]
inputs = tok(questions, padding=True, truncation=True, return_tensors="pt")
with torch.no_grad():
    before = model(**inputs).logits
merged = model.merge_and_unload().eval()
with torch.no_grad():
    after = merged(**inputs).logits
max_diff = float((before - after).abs().max())
assert torch.allclose(before, after, atol=1e-5), max_diff
merged.save_pretrained(ROOT / "merged")
tok.save_pretrained(ROOT / "merged")
smoke = {
    "merge_max_abs_logit_difference": max_diff,
    "merge_equivalent_atol": 1e-5,
    "examples": [
        {"question": q, "predicted": report["labels"][i]}
        for q, i in zip(questions, after.argmax(-1).tolist())
    ],
}
(ROOT.parent / "reports/router-smoke.json").write_text(json.dumps(smoke, indent=2))
if len(sys.argv) > 1:
    with torch.no_grad():
        probs = merged(
            **tok(sys.argv[1], return_tensors="pt", truncation=True, max_length=64)
        ).logits.softmax(-1)[0]
    print(
        json.dumps(
            {
                "question": sys.argv[1],
                "route": report["labels"][int(probs.argmax())],
                "score": float(probs.max()),
                "note": "Softmax score is not calibrated confidence.",
            }
        )
    )
else:
    print(json.dumps(smoke, indent=2))
