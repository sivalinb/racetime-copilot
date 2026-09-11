# YouTube interval test — 05:00–08:00

**Recorded 10 September 2026: direct YouTube analysis succeeded without a video upload.** RaceTime produced seven timestamped observations and a five-sentence cited recap for the requested three-minute interval. The job paused at `awaiting_review`; no human approval or independent accuracy score is claimed.

## Test setup and outcome

| Item | Recorded value |
|---|---|
| Source | [YouTube video S_9wb3g7jtY](https://www.youtube.com/watch?v=S_9wb3g7jtY) |
| Interval / spoiler cutoff | 05:00–08:00 / 08:00 (300–480 / 480 seconds) |
| Question | What happened in this interval? Describe what is visible or heard; do not invent runner identities. |
| Input | Public YouTube URL sent directly to Gemini; no user upload |
| Test path | Existing `scripts/verify_video.py`, Service and LangGraph workflow; isolated local runtime |
| Result | `awaiting_review`; error `null`; seven observations; five cited sentences |
| Recorded coverage | `[300, 480]`; no reported gaps. This does not measure event completeness. |
| Summary mode | `generated_verified`: separate model grounding check accepted the recap |
| External tracing | Disabled for this run; local agent trace saved |
| Code under test | `7a7e540c330f815e0d2e0bdc2396635c57a5c1b8` |

## AI-generated recap

These are model observations of the speaker's commentary, not independently verified registration facts. Source timestamps are approximate until reviewed. The segment shows a speaker discussing races, rather than footage of athletes competing.

| Time | Reported content |
|---|---|
| [05:00–05:43](https://www.youtube.com/watch?v=S_9wb3g7jtY&t=300) | Mingus Traverse 80 route: Jerome, Verde River, Dead Horse State Park, Tuzigoot, Lime Kiln Trail and the Sedona finish. |
| [05:43–06:00](https://www.youtube.com/watch?v=S_9wb3g7jtY&t=343) | The speaker checks the live chat and invites audience questions. |
| [06:00–07:08](https://www.youtube.com/watch?v=S_9wb3g7jtY&t=360) | Bradshaw Brute route follows the first 100 miles of the 250 course; the speaker reports 75 registrations versus 162 for Mingus Traverse. |
| [07:08–07:31](https://www.youtube.com/watch?v=S_9wb3g7jtY&t=428) | The speaker reports 449 Cocodona 250 registrations and briefly pauses after sneezing. |
| [07:31–08:00](https://www.youtube.com/watch?v=S_9wb3g7jtY&t=451) | Sedona Canyons 125: 485 registrations, 394 on the waitlist and discussion of a possible lottery next year. |

The provider notes that race-course visuals are absent and the speaker's identity is not explicitly confirmed.

## What happened in the background

1. **Retrieve:** the agent found zero existing observations in the fresh runtime.
2. **Inspect:** Gemini analyzed the requested 300–480-second window and returned timestamped notes.
3. **Retrieve again:** seven observations were selected after embedding and time-filtered retrieval.
4. **Plan:** the model chose `summarize` from the permitted actions.
5. **Summarize and check:** the narrative referenced stored evidence IDs and passed the separate model grounding check (`generated_verified`).
6. **Pause for review:** the graph saved the recap at `awaiting_review`. This run did not approve/reject or test review after restart.

[Download the recorded JSON: observations, citations and local trace](https://github.com/sivalinb/racetime-copilot/blob/main/evals-observability/observability/examples/youtube-S_9wb3g7jtY-05m-08m.json).

## Reproduce in Streamlit

1. Open **Video workspace** and sign in. Under **Videos**, paste the source URL and click **Save video**.
2. In **Ask / inspect**, select that video and **Ask the agent**.
3. Set **Start `05:00`**, **End `08:00`**, and **Spoiler cutoff `08:00`**.
4. Ask: **What happened between 05:00 and 08:00? Summarize the main updates.**
5. Click **Queue job**, then open **Jobs / results**. Review timestamps before approving or rejecting.

Set the time fields explicitly: times typed in the question do not change those fields. The original test ran outside the signed-in Streamlit account; this report is a saved example, not a job in your account. A rerun creates a new result and may differ.

## Reproduce from the repository

With dependencies installed and `GEMINI_API_KEY` configured in the ignored `.env`:

```bash
LANGSMITH_TRACING=false RACETIME_DATA_DIR="$PWD/.runtime/youtube-recheck" \
  .venv/bin/python scripts/verify_video.py \
  --url 'https://www.youtube.com/watch?v=S_9wb3g7jtY' --start 300 --end 480
```

This makes billable provider calls and writes `real-video-check.json` in that runtime directory. Use a fresh runtime directory for a cold-source check. The CLI uses the exact recorded question; the Streamlit example above expresses the same user intent.

## What this proves, and what remains

- **Demonstrated:** one direct YouTube interval completed extraction, semantic retrieval, bounded planning, cited generation, model grounding check and the pending review checkpoint.
- **Not measured:** independent factual correctness, timestamp error, event recall, spoiler leakage against independently watched footage, end-to-end latency or cost.
- **Still pending:** varied real-video cases, larger-file processing, an active livestream test and restored LangSmith ingestion. A prior different YouTube source (`qnVos4_1soM`, 10:00–11:00) failed with HTTP 500; this success does not establish universal URL reliability.
- **Dataset boundary:** this is an integration record. Model-generated notes are not golden answers, and this case is not added to the 40-case synthetic benchmark or counted as a human-reviewed evaluation.
