# How RaceTime applies Week 1–5

Follow each week from **learning → implementation → what to try → evidence**. The nested bullets explain exactly how the feature demonstrates the concept.

**Before you start:** open Video workspace and sign in. For a video walkthrough, use a short MP4 under 12 MB or the successful [YouTube 05:00–08:00 example](https://github.com/sivalinb/racetime-copilot/blob/main/reports/youtube-interval-test.md). Some sources have encountered provider errors. For the key-free examples below, switch to Evidence demo and select the fictional Canyon Relay race.

All five learning themes are represented. Remaining validation and submission items are stated separately; this is not a claim that every assignment is complete.

## Week 1 — Build a useful app with AI assistance

- **Define a real problem and turn it into a product.**
  - **How it covers the learning:** your problem—missing part of a long race broadcast—becomes a specific input and output: a source, a time interval and a question produce a recap with evidence.
  - **Follow through:** open How to use, then Videos. Point to the URL/upload controls and explain who benefits: race viewers, families and organizers.

- **Build an interactive Streamlit application.**
  - **How it works:** Streamlit collects the video, interval and question; Python validates the request and saves a background job.
  - **Follow through:** save a clip at least 30 seconds long. In Ask / inspect, select Ask the agent; set Start `00:00`, End `00:30` and cutoff `00:30`. Ask “What happened in these 30 seconds?” and click Queue job.
  - **Evidence:** Jobs / results shows the saved request and its status. A provider error demonstrates the failure path, not a successful analysis.

- **Iterate using structured prompts and feedback.**
  - **How it covers the learning:** your requests for simpler instructions, example questions and a collapsed learning map led to concrete interface changes.
  - **Follow through:** show one request from your development conversation and the resulting screen. Explain what was unclear before and how the change helps a user.
  - **Submission evidence:** include actual prompts, iterations and screenshots in the development record, plus a short working-demo recording. Those submission materials are still to be completed.

- **Apply the course's custom-app path.**
  - **Why it fits:** Week 1 allows your own application and framework. RaceTime applies AI-assisted prototyping through Streamlit rather than reproducing the sample stock-portfolio CSV project.
  - **Code to follow:** [app.py](https://github.com/sivalinb/racetime-copilot/blob/main/app.py) selects the workspace; [racetime/ui.py](https://github.com/sivalinb/racetime-copilot/blob/main/racetime/ui.py) contains the video forms and results.

## Week 2 — Retrieve evidence before generating an answer: RAG

- **Ingest a source and divide it into useful pieces.**
  - **How it works:** a recorded-video request is inspected in windows of up to 300 seconds. Gemini returns individual observations containing start/end times, text and a type such as visual or commentary. These notes are the retrievable pieces; the app does not embed the entire video as one text document.
  - **Follow through:** run the short-clip question from Week 1. Open the completed job's result JSON and find `selected`. Inspect an observation's `start`, `end`, `text` and `kind`.
  - **Evidence:** source observations are structured and tied to an interval. In Evidence demo, VTT/SRT/JSON imports provide an alternative ingestion path.

- **Create embeddings and store knowledge for reuse.**
  - **How it works:** Gemini Embedding 2 converts each observation's text into a 768-number vector. SQLite stores the observation and vector together. The question is embedded too, so the app can compare meaning rather than relying only on identical words.
  - **Follow through:** inspect `embed()` in [racetime/provider.py](https://github.com/sivalinb/racetime-copilot/blob/main/racetime/provider.py), then `save_window()` in [racetime/store.py](https://github.com/sivalinb/racetime-copilot/blob/main/racetime/store.py).
  - **Evidence:** real document/query embedding requests passed. The vectors are stored internally; they are not displayed as a separate app screen.

- **Retrieve relevant evidence with time and spoiler filters.**
  - **How it works:** retrieval keeps only observations fully inside Start–End and available by the cutoff. It ranks eligible vectors by similarity, selects up to 30 observations initially, and retains related annotated conflicting claims when relevant.
  - **Follow through:** ask a second question about the same interval, such as “What was visible, rather than mentioned in commentary?” Inspect `selected` and the `retrieve` entry in `trace`.
  - **Evidence:** the selected notes should satisfy the time rules. Whether their ranking answers the question well still needs human evaluation. A new question does not guarantee the planner will avoid another inspection.

- **Generate a cited answer and handle missing evidence.**
  - **How it works:** Gemini writes sentences with observation IDs. Unknown IDs are rejected, and a separate model call checks support. If generation fails, the app can show labelled extracts; if evidence is insufficient, it can return a clarification message.
  - **Follow through:** compare a recap sentence with its referenced observation, then click the timestamp or Play evidence. Check the original footage yourself.
  - **Evidence and limit:** this demonstrates grounding mechanics. A valid citation or second AI check can still support an incorrect observation; real-race accuracy is not yet established.

- **Connect the steps into a complete RAG chain.**
  - **Follow the code:** [service.py](https://github.com/sivalinb/racetime-copilot/blob/main/racetime/service.py) ingests and stores notes; [provider.py](https://github.com/sivalinb/racetime-copilot/blob/main/racetime/provider.py) embeds and generates; [agent.py](https://github.com/sivalinb/racetime-copilot/blob/main/racetime/agent.py) retrieves and coordinates the answer.
  - **Current proof:** a six-second synthetic uploaded video and one direct YouTube interval passed extraction, learned retrieval and cited recap integration. The YouTube run returned seven observations and paused for review; [report and trace](https://github.com/sivalinb/racetime-copilot/blob/main/reports/youtube-interval-test.md). Broader URL/large-file reliability and independently reviewed race cases remain open.

## Week 3 — Build an agent with decisions, tools and state

- **Choose the next action instead of making one isolated model call.**
  - **How it works:** the graph first retrieves evidence. A cold recorded source must be inspected. When multiple actions are legal, Gemini chooses among inspecting, summarizing or clarifying; rules cap the choices and iterations.
  - **Follow through:** in Jobs / results, expand the result JSON and inspect `trace`. Look for `step: plan`, `action`, `reason` and `mode`.
  - **Evidence:** `mode: llm` identifies a model decision; `rule` identifies a fixed control-flow decision; `fallback` identifies recovery from a failed planner call. Not every step is autonomous.

- **Use tools for distinct jobs.**
  - **How it works:** retrieve searches notes; inspect reads the chosen video interval; summarize produces a cited answer; clarify explains insufficient evidence.
  - **Follow through:** match each trace step to the evidence or output it produced. For example, inspect should be followed by retrieval of the newly saved observations.
  - **Why it fits:** this is one agent using tools and graph steps. It does not claim that each step is a separate independent agent.

- **Remember progress across steps and restarts.**
  - **How it works:** LangGraph state keeps the question, interval, selected evidence, decisions and recap. SQLite checkpoints save graph progress; a separate SQLite job record tracks queued/running/review status.
  - **Follow through:** return to Jobs / results after signing out and back into the same local account. Confirm that your saved job remains. This demonstrates account persistence; the separate restart tests demonstrate checkpoint recovery.
  - **Evidence:** [product_test.py](https://github.com/sivalinb/racetime-copilot/blob/main/tests/product_test.py) includes durable-review and recorded-job lease-recovery tests.

- **Recover from errors and prevent endless work.**
  - **How it works:** eligible transient provider errors get one retry. Default limits allow 32 generation/embedding calls per job; the graph also bounds its iterations. Failed grounding can produce an explicit extractive fallback.
  - **Follow through:** in Evidence demo, select Simulate one retrieval failure, then Create recap. Inspect the retry in the trace. This is a controlled retrieval demonstration, not a live Gemini outage test.
  - **Evidence:** the Python tests separately check planner fallback, generation failure and call budgets. Real provider failures remain visible rather than being replaced with invented success.

- **Hand control to a human before accepting a recap.**
  - **How it works:** `interrupt()` pauses the video graph at review. Approving or rejecting resumes the saved graph and records your decision.
  - **Follow through:** find an `awaiting_review` job, check its source timestamps, click Approved or Rejected, and confirm `completed` plus the recorded decision.
  - **Evidence:** durable review passed automated restart tests and a real small-video integration run. Approval records a person's decision; it is not a factual-accuracy guarantee.

## Week 4 — Measure quality, inspect failures and compare improvements

- **Define expected behavior with a repeatable dataset.**
  - **How it works:** 40 authored synthetic cases specify expected evidence IDs for full cues, clipped cues, gaps, delayed observations and untrusted instructions.
  - **Follow through:** open [golden-cases.json](https://github.com/sivalinb/racetime-copilot/blob/main/reports/golden-cases.json). Choose a case and compare its question/time range with `expected`.
  - **Evidence:** expected behavior is specified before scoring. These are synthetic evidence tests, not independent labels for real video.

- **Compare a baseline with the candidate workflow.**
  - **How it works:** the baseline accepts overlapping observations. The candidate applies stricter interval, availability and instruction rules. Both run on the same cases; exact evidence-ID matches determine a pass.
  - **Follow through:** in Evidence demo → Capstone learning → Evidence evaluation, compare `baselinePassed` and `passed`. For case-level detail, open [workflow-evaluation.json](https://github.com/sivalinb/racetime-copilot/blob/main/reports/workflow-evaluation.json) and compare `expected`, `baseline` and `actual`.
  - **Measured result:** 20/40 baseline versus 40/40 candidate. That is 50% versus 100% on this dataset, not 100% race-summary accuracy.

- **Explain which failures a change addresses.**
  - **How it works:** excluding partially overlapping cues addresses boundary leakage; checking availability addresses late reports; filtering obvious source instructions addresses those test inputs.
  - **Follow through:** inspect a `clipped-...` case, `delayed`, and `untrusted-instruction`. Explain why the baseline and candidate differ in each one.
  - **Remaining work:** this comparison is not a separate ablation of each change. The full Week 4 improvement report still needs targeted before/after runs and reviewed failure analysis on the video agent.

- **Measure quality together with operating behavior.**
  - **How it works:** the synthetic report includes p50/p95 execution time and traces. Video jobs record provider calls and generation-token usage. Zero provider calls in the evidence benchmark describe that local extractive workflow only.
  - **Follow through:** inspect `p50Ms`/`p95Ms` in Evidence evaluation. In Video workspace, read the sidebar usage summary and a job's trace.
  - **Limit:** local synthetic timings are not a production latency promise, and generation-token counts do not include all provider charges. External LangSmith trace verification is blocked by monthly quota.

- **Collect human judgments for real footage.**
  - **How it works:** Evaluation records expected facts, supported-sentence percentage, missed events, spoiler leaks and largest timestamp error.
  - **Follow through:** independently watch the chosen interval, select its recap in Video workspace → Evaluation, enter your judgments and save them. Do not tick the reviewed checkbox without watching.
  - **Next evidence:** aggregate saved reviews with the documented evaluation command. Reviewed race cases and verified LangSmith case/model/tool traces remain necessary before claiming full video-agent evaluation coverage.

## Week 5 — Train and evaluate a focused model with LoRA

- **Define a narrow task and labelled examples.**
  - **How it works:** the separate experiment predicts four question intents: recap, runner, verify and compare. For example, “Any news about bib 42?” belongs to runner.
  - **Follow through:** open [training/dataset.json](https://github.com/sivalinb/racetime-copilot/blob/main/training/dataset.json). Compare an example's text, label and split.
  - **Evidence:** 144 authored training examples and 40 separately worded held-out examples are recorded. Held-out examples do not enter optimizer updates.

- **Train adapters while keeping the base encoder frozen.**
  - **How it works:** PEFT adds rank-8 LoRA adapters to BERT-tiny's query/value layers. The classifier head also trains. This applies specialization without updating all base-model weights.
  - **Follow through:** inspect `LoraConfig`, `requires_grad` and the optimizer in [train_router.py](https://github.com/sivalinb/racetime-copilot/blob/main/training/train_router.py).
  - **Evidence:** the report records trainable parameters, initial/final loss and training steps. Low training loss alone does not demonstrate useful generalization.

- **Make a fair comparison on unseen examples.**
  - **How it works:** both arms start from the same pretrained encoder and seeded classifier head, use the same data and run 96 optimizer steps. Both train the head; only the LoRA arm also trains adapters.
  - **Follow through:** open Evidence demo → Capstone learning → LoRA routing evaluation. Compare frozen-encoder and LoRA accuracy, macro F1 and confusion matrices.
  - **Measured result:** accuracy rises from 52.5% to 70%, a 17.5 percentage-point improvement. The LoRA model still misroutes 12 of 40 held-out questions; inspect the full report's `predictions` to find them.

- **Merge the adapter and smoke-test inference.**
  - **How it works:** `merge_and_unload()` folds the learned adapter into the base weights. The script compares model outputs before and after merging, then runs sample classifications.
  - **Follow through:** open [router-smoke.json](https://github.com/sivalinb/racetime-copilot/blob/main/reports/router-smoke.json). Check the merge difference against the tolerance and inspect the four sample predictions.
  - **Evidence:** maximum output-logit difference was about `9.54e-7`, within the `1e-5` tolerance. [training/infer.py](https://github.com/sivalinb/racetime-copilot/blob/main/training/infer.py) implements this check.

- **Explain the scope of the specialization honestly.**
  - **How it covers the learning:** labelled data → LoRA training → held-out evaluation → merge → inference are demonstrated in the race domain.
  - **What it does not do:** this BERT encoder classifier is separate from the running app. It does not watch footage or generate recaps, and its predictions do not currently control the video agent.
  - **Course distinction:** this is an adapted experiment, not the exact Qwen3/LLaMA Factory support-ticket exercise. Custom exploration is allowed by the handout; real-user quality, speed and cost benefits remain unproven.

## Your presentation in one sentence

> “I built a usable app in Week 1, connected answers to evidence in Week 2, added controlled agent decisions and human review in Week 3, measured behavior in Week 4, and tested a specialized router in Week 5—with the evidence and remaining gaps visible for each.”
