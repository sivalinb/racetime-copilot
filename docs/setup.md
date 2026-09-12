# Setup and external accounts

## 1. Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_product.py
```

Open http://localhost:8501. This starts the video workspace and background worker. Create a local account to retain your videos and results across refreshes.

For the original evidence demo too, install Node.js 22.13+, run `npm ci`, then use `python scripts/run_demo.py` instead. Run one launcher at a time.

## 2. Gemini

1. Create a key at https://aistudio.google.com/apikey.
2. Put `GEMINI_API_KEY=your_key` in the project `.env`. Never commit it or paste it into chat.
3. Set `GEMINI_MODEL` and `GEMINI_EMBED_MODEL` only if your account needs a different supported model.
4. Restart the launcher after configuration changes.
5. Run `python scripts/provider_check.py`. This makes small generation and embedding requests and records a result under `.runtime/`.

Provider use can incur charges. Defaults limit each job to 32 generation/embedding calls, each account to 120 calls per 24 hours, three queued/running jobs, and 100 MB per upload. Failed requests count toward the call budget. Files API operations and provider-side token accounting are additional; Google billing is authoritative. No dollar estimate is shown without a verified price configuration.

## 3. Analyze a video

Save a public YouTube URL or upload an MP4, MOV or WebM. Choose a short interval first. `Ask the agent` retrieves existing evidence, decides whether another inspection is useful, creates a cited summary, checks grounding and pauses for review. Approve or reject under Jobs / results.

YouTube access depends on provider support and the video's availability. Private, restricted or unavailable videos fail explicitly. Small MP4 uploads up to 12 MB use inline input; larger uploads use the Files API. The small inline path and one direct YouTube interval (05:00–08:00 of `S_9wb3g7jtY`) passed integration testing. An earlier different YouTube source and Files API processing returned server errors; larger-upload processing remains unverified. [Recorded YouTube test](../reports/youtube-interval-test.md). Uploaded videos are the alternative; the app does not bypass access controls.

## 4. Live capture

Save a currently live public YouTube URL. Choose Capture a live stream. Enter the broadcast's current elapsed time as Start and up to 15 minutes later as End/cutoff.

The worker captures continuously into 60-second segments while it analyzes completed segments. Live processing can lag behind capture. Only successfully processed windows can be queried. Offsets depend on the elapsed time entered at capture start; network/broadcast delays can affect alignment. Interrupted captures retain processed evidence and require a new capture with the current elapsed time. The app does not promise reconstruction of footage it never captured.

## 5. LangSmith

Create a key at https://smith.langchain.com and add these values to `.env`:

```text
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_key
LANGSMITH_PROJECT=racetime-copilot
LANGSMITH_TRACING_SAMPLING_RATE=1.0
```

Restart the worker and run a video question. Verify the job's graph run in LangSmith. This sends workflow inputs and evidence to LangSmith. Local job traces remain available without this account. If ingestion reports a monthly quota limit, check LangSmith Settings and restore quota or wait for its reset. Set LANGSMITH_TRACING=false and restart to use local traces meanwhile. Do not keep retrying an exhausted quota.

Jobs / results includes **Open LangSmith trace** for traced results. The root identifies the job and interval; expand it for graph decisions, retrieval, video inspection, Gemini generation and embeddings. Generation spans contain reported token usage; raw video bytes, upload paths and SDK credentials are omitted from custom spans. The trace still contains questions and generated evidence. An approve/reject action creates a separate review trace linked to the original result.

Run `python -m scripts.check_langsmith` once to verify hosted ingestion and nested spans using synthetic SDK responses. It consumes three LangSmith traces, makes no Gemini calls, and saves a private report to `.runtime/langsmith-check.json`. Fixture tokens and observations are not real-video measurements. The app's trace link means tracing was requested; only a successful hosted readback confirms ingestion. See [the observability walkthrough](../evals-observability/observability/README.md#langsmith).

## 6. Real-video evaluation

Independently watch selected race intervals. In Evaluation, record expected facts, supported sentences, missed events, timestamp error and spoiler leaks. Export individual annotations, or aggregate them with:

```bash
python scripts/evaluate_real.py
```

The command fails when no reviewed examples exist. Begin with 10 intervals covering clear action, missing footage, uncertain identity and conflicting timing. Keep human labels separate from model output. Do not publish a real-quality score until those reviews exist.

## 7. Public deployment

The Docker/Caddy configuration in `deployment/` is a prepared deployment path. It needs a Linux host with Docker, a domain pointing to that host, and Google OIDC credentials. It has not been deployed merely by creating these files.

1. In Google Cloud, configure an OAuth web client and allow `https://YOUR_DOMAIN/oauth2callback`.
2. Copy `deployment/secrets.example.toml` to `.streamlit/secrets.toml`. Set the client ID, client secret, redirect URI and a locally generated random cookie secret.
3. Add `RACETIME_ALLOWED_EMAILS=you@example.com` to `.env`. Public sign-in requires a verified, allow-listed email.
4. Set `RACETIME_DOMAIN` in your shell and run `docker compose -f deployment/compose.yml up --build -d`.
5. Verify HTTPS, sign-in, account isolation, a real job, restart recovery and a backup restore before inviting users.

The public image serves only the Python video workspace. It fails closed without OIDC; local password registration is not exposed publicly. Use one application container and one worker with the mounted SQLite volume. Horizontal scaling requires a shared job/database design.

Back up the database with `python scripts/backup.py /path/to/backup` and separately back up `.runtime/uploads/` and `.runtime/evaluations/`. Public hosting, DNS and OIDC credentials require your account access; do not send passwords or API keys in chat.

## 8. Week 5 exact tooling

The completed LoRA experiment uses BERT-tiny. The Week 5 handout's exact Qwen3-1.7B-Base/LLaMA Factory exercise is a separate support-ticket task and is explicitly optional for the certificate. If your instructor requires that exact exercise, use the course notebook with a T4 runtime and the labelled `support_tickets.csv`; those inputs are not in this race project. No Qwen training result is claimed here.
