# Verification record - 10 September 2026

- TypeScript: passed.
- Production build: passed (Vinext static route-classification notice is informational).
- Lint: passed. Native image tags intentionally serve local illustrations; custom Input/Textarea components are recognized as label controls.
- Unit tests: 17 passed, zero failures.
- Synthetic evidence evaluation: 40/40; naive-overlap baseline 20/40. See per-case reports.
- API integration: import, recap, cross-session source and review isolation, approval, live append, stale-revision rejection, unavailable-range rejection and persisted history passed.
- Browser: fictional recap, conflict display, saved approval, transcript import and WebMCP `summarize_interval` passed; narrow-layout visual review completed.
- LoRA: 144 training / 40 held-out authored requests; baseline accuracy 52.5%, LoRA 70.0%; merge max absolute logit difference 9.54e-7.
- Dependency audit: zero known advisories in the recorded npm audit.
- Streamlit: real-backend AppTest passed initial render, recap, conflicts, spoiler exclusion, review, invalid cutoff, retry, transcript import, live import/append, revision refresh, cache and current history. Browser recap and visual review passed.
- Brochure: simplified from 15 to six pages, preserving personalized illustrations; all six pages rendered and visually reviewed.
- Simplification: app.py and requirements.txt are the canonical demo entry points; launcher, CI and AppTest references updated. Streamlit integration passed after the rename.

Not verified: real YouTube video understanding, automatic livestream ingestion, external LangSmith traces, independent human-reviewed dataset quality, public hosted deployment or real-user pilot benefit. GitHub Actions results are separate from the local checks above.

## Local video product extension

- Python product contracts: **21 passed** using real SQLite/LangGraph and controlled provider fixtures. Includes cold-source inspection, account isolation, durable review, lease recovery, cancellation, call budgets, fractional intervals, missing coverage, limitation propagation, stale evidence replacement and schema/error handling.
- Video Streamlit AppTest: **1 passed** for local registration, saving a source, queuing and cancellation. Original evidence Streamlit suite also passed after the extension.
- Real Gemini: `gemini-3.5-flash` generation and `gemini-embedding-2` document/query embeddings passed (768 dimensions).
- Real inline video: generated a six-second synthetic clip, red for 0–3 seconds and blue for 3–6 seconds. Gemini returned those two observations and a cited recap. The graph paused for review and a new service process resumed with rejection. This checks integration, not human approval or race accuracy.
- Shared YouTube race interval 600–660 seconds: failed HTTP 500 with Gemini 3.5 and 3.8 Flash. Gemini 2.5 Flash returned HTTP 404 for this account. No successful race-video result is claimed.
- Files API: an upload returned PROCESSING, but subsequent processing checks returned HTTP 500. Larger-upload end-to-end support remains unverified. Small MP4s use the tested inline path.
- LangSmith: key configured outside Git. Trace ingestion rejected with HTTP 429 because monthly unique-trace quota was exhausted. Local demo launched with external tracing disabled; the key/configuration are retained for a later retry.
- Active livestream validation deferred by the user because no active race URL is available. No clock-alignment or real-race quality score is claimed.
- Six-page brochure updated and all pages rendered and visually inspected. Public hosting is deferred; no Docker build or hosted OIDC success is claimed.
