# LangSmith instrumentation check

Checked 11 September 2026. This is an instrumentation report, not a video-quality evaluation.

| Check | Result |
|---|---|
| Saved-key authentication | Succeeded |
| `racetime-copilot` project creation | Succeeded |
| Synchronous synthetic trace write | Blocked: `LangSmithRateLimitError`, HTTP 429, monthly limit |
| Hosted trace query after the attempted synthetic workflow | No runs found; hosted nesting/token verification did not pass |
| Real graph with SDK transport intercepted locally | Passed: job → graph → retrieval/inspection/embedding/generation spans |
| Four synthetic generation calls | Passed: child parent IDs, fixture input/output/total tokens and explicit input filtering |
| Human-review resume | Passed locally; the synthetic recap was rejected and the job completed |
| Fail-open tracing and sanitized error handling | Passed locally |
| Python product, instrumentation and video UI tests | 27 tests passed |

No Gemini calls or actual video analysis were performed by this check. Fixture token counts are 10 input + 5 output per generation; they are test data, not measured provider usage. The earlier recorded YouTube run remains separate.

Reproduce the local checks:

```bash
python -m unittest discover -s tests -p observability_test.py
```

After resolving the monthly limit, run the hosted check once:

```bash
python -m scripts.check_langsmith
```

That check sends three synthetic traces, then verifies hosted span types, parent IDs, token counts and review completion. It writes `.runtime/langsmith-check.json`, which remains private and ignored by Git. Do not report hosted observability as verified until the command succeeds.

Next, analyze a short interval in Streamlit and open its LangSmith trace. Independently reviewing that video's facts is still a separate evaluation step.
