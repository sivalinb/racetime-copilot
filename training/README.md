# LoRA intent-router lab

This separate experiment adapts the Week 5 specialization technique to four race-viewer intents: recap, runner, verify and compare. It is an **encoder classifier**, not a video model or a generative LLM. The video app uses a bounded Gemini planner with application rules; this trained classifier is not deployed in that graph. See the [Week 1–5 completion checklist](../docs/course-completion-audit.md) for demonstrated learning and remaining submission evidence.

## Reproduce

Python 3.12 was used. This downloads the small `prajjwal1/bert-tiny` base model and the compatible `google-bert/bert-base-uncased` tokenizer from Hugging Face.

```bash
python3 -m venv .venv
.venv/bin/pip install -r training/requirements-lock.txt
.venv/bin/python training/train_router.py
.venv/bin/python training/infer.py
.venv/bin/python training/infer.py 'Compare those two race sections.'
```

The script writes the authored dataset, adapter, held-out report, merged model and inference smoke report. Base weights, downloaded caches and merged weights remain ignored. The trained small adapter is included under `model/adapter/` for inspection; a fresh run uses `training/checkpoints/adapter/`.

## Fair comparison and results

Both arms start with the same pretrained encoder and seeded classification head. Both train the classifier on the same 144 synthetic requests, for 96 optimizer steps. The LoRA arm additionally trains rank-8 query/value adapters. Forty separately worded requests are held out; none enter optimizer updates.

| Arm | Accuracy | Macro F1 |
|---|---:|---:|
| Frozen encoder + trained head | 52.5% | 0.522 |
| LoRA encoder + trained head | 70.0% | 0.709 |

The full report includes per-class precision/recall/F1, confusion matrices and every held-out prediction. Merge/inference smoke checks preserved logits within `1e-5` absolute tolerance.

This is one small synthetic split and one seed, without independent human labeling. Low training loss does not establish generalization: 12/40 held-out requests were still misrouted. The comparison is against a frozen-encoder classifier, not against a frontier LLM. A handout-exact Qwen3-1.7B / LLaMA Factory version remains a future extension.
