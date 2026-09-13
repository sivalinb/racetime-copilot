# Recorded Safari demonstration

The completed **5:00 captioned MP4** shows the local Streamlit product, hosted Braintrust traces, Nebius Token Factory and the separate Week 5 LoRA lab. It uses actual Safari screen-recording footage. Idle sections were removed and playback pacing was adjusted; explanatory captions were added. The original had no audio track.

The file is prepared locally as `RaceTime-Copilot-Safari-Demo-5min.mp4`, with an editable `.srt` subtitle file. It has not been published at a shareable video URL. Attach or share the MP4 when submitting, and confirm the instructor accepts that format where a handout asks for Loom.

## Follow the five-minute flow

| Video time | What is shown | Supporting evidence |
|---|---|---|
| 00:00–00:28 | Missed-broadcast problem; save a public YouTube link | [Product guide](../docs/how-to-use.md) |
| 00:28–01:08 | Ask about 05:00–08:00; background processing and architecture | [Agent](../racetime/agent.py), [architecture](../docs/architecture.md) |
| 01:08–01:28 | Cited recap, limitations and pending human review | [Saved demo result](../evals-observability/observability/examples/safari-video-demo.json) |
| 01:28–01:58 | Fresh video job in Braintrust, including Gemini calls and timing | [Hosted video trace](https://www.braintrust.dev/app/siva-project/object?object_type=project_logs&object_id=f1a828a0-8dd9-4519-9839-49740bc5523e&id=420bedb2-00f2-409a-b468-f384988375b5) |
| 01:58–02:37 | Earlier Nebius fixture trace; shared Qwen endpoint in Token Factory | [Verified fixture trace receipt](../evals-observability/observability/examples/braintrust-nebius-check.json) |
| 02:37–02:49 | Independent-label and human-evaluation controls | [Evaluation protocol](../docs/week4-evaluation.md) |
| 02:49–03:47 | Actual LoRA losses, comparisons, five smoke examples, errors and local classification | [Week 5 guide](../docs/week5-demonstration.md) |
| 03:47–05:00 | Learning map, GitHub evidence, judge disagreement and future applications | [Handout audit](../docs/course-completion-audit.md), [judge report](../evals-observability/benchmarks/nebius-judge-smoke-recorded.json) |

## What this run establishes

- Source: [public YouTube race briefing](https://www.youtube.com/watch?v=S_9wb3g7jtY), 05:00–08:00, cutoff 08:00. No upload was required.
- Job `6e0b33c0-4ccc-4b25-aa13-c11bad1a7625` produced **eight observations** and reached `awaiting_review`. It describes a speaker discussing races, not footage of an active race. No independent factual approval was performed.
- Braintrust's hosted UI showed the video job, nested inspection/retrieval/planner/generation/embedding/summary spans, **34.04 seconds** and an aggregate **25,719 tokens**. Those displayed tokens differ in scope from the local generation counter and are not a reconciled bill.
- The supplied Braintrust project ID displays as **My Project**. The app's `racetime-copilot` configuration label does not rename the remote project. Hosted trace links require project access.
- The Nebius trace shown is an **earlier authored-fixture check**, not an independent judge run on this fresh video recap. Its 294 input / 159 output tokens and roughly 5.4 seconds are recorded separately.
- The LoRA classifier returned `compare` for “Compare those two race sections.” It remains separate from the video agent; its softmax output is not calibrated confidence.

The [earlier YouTube report](youtube-interval-test.md) records **seven observations** from a different run on the same interval. Neither run is an independent accuracy benchmark. Active livestream capture, broad source reliability and reviewed real-video quality remain unvalidated.
