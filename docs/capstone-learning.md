# How RaceTime applies Week 1–5

**One race-viewing problem connects all five weeks:** build an app, give it evidence, let an agent choose its next step, measure its behavior, and experiment with a specialized model.

This map follows your Week 1–5 handouts. It shows demonstrated learning, not a claim that every assignment or submission requirement is complete.

| Week | Learning in simple terms | RaceTime application | Current coverage |
|---|---|---|---|
| 1 | Turn an idea into a working app with AI coding help | Streamlit screens for videos, questions, results and review | Working custom app; follows the handout's own-app path |
| 2 | Find relevant evidence before answering: RAG | Timestamped notes, learned embeddings, retrieval and cited recaps | Implemented; small-video integration verified; race accuracy still needs review |
| 3 | Build an agent that chooses actions and keeps state | Retrieve, inspect, summarize or clarify; retries and durable human review | Implemented and tested; usefulness on real race cases remains to be measured |
| 4 | Measure quality and failures instead of relying on a demo | Synthetic cases, baseline comparison, traces and human evaluation screen | Partially demonstrated; real labels and verified LangSmith evaluation remain |
| 5 | Teach a small model a focused task with LoRA | Separate race-question intent-router experiment | Adapted training, evaluation and merge completed; not used by the live app |

## Week 1 — Build a useful app with AI assistance

**What you learned:** describe a problem, use an AI coding assistant to prototype it, and improve the interface through feedback.

**How RaceTime applies it:** your race-viewing idea became a Streamlit app. You can save a source, choose times, ask a question, inspect results and record a review. The changes from your feedback—simpler documentation, example prompts and these help sections—show iterative development.

**Why it fits:** Week 1 explicitly permits your own app and framework. A stock-portfolio CSV is the sample project, not a requirement for this custom path.

**Show it:** walk through the interface and explain one prompt you used and one improvement it produced. The repository supplies the code; the submission still needs the required development record and short demo recording.

## Week 2 — Answer from evidence using RAG

**What you learned:** bring in a knowledge source, divide it into useful pieces, embed and store them, retrieve relevant pieces, then generate an answer with citations.

**How RaceTime applies it:** the knowledge source is race footage. Gemini turns a selected interval into timestamped observations. Learned embeddings represent the notes for semantic search, and SQLite stores them. Retrieval selects notes relevant to your question while enforcing the time window and spoiler cutoff. The answer cites those notes and can report insufficient evidence.

**Why it fits:** it implements the ingest → chunk → embed → store → retrieve → generate chain, adapted from documents to video observations. The key-free Evidence demo has a separate caption/import pipeline with deterministic ranking.

**Show it:** ask about a short interval, open its cited observations, and follow a timestamp back to the source. A small synthetic video passed the full integration. YouTube processing errors and independent race factual/retrieval evaluation remain unresolved; a citation alone is not proof of correctness.

## Week 3 — Build an agent with decisions, tools and memory

**What you learned:** an agent chooses what to do next, uses tools, remembers progress, handles failures and involves a human.

**How RaceTime applies it:** LangGraph holds the question, interval, evidence and progress. Rules restrict the available actions; Gemini chooses among them when there is a choice. The graph can retrieve, inspect, summarize or clarify. Call budgets and retries bound the work. A real human-review interrupt saves a checkpoint in SQLite and resumes after a restart.

**Why it fits:** the answer comes from a stateful workflow with decisions and recovery. This is a single agent with tools; separate graph steps are not presented as independent agents. The handout allows choosing an appropriate agent pattern for your own use case.

**Show it:** open a result's activity trail, explain the chosen actions, then approve or reject its saved recap. Durable review has passed restart tests, including a real small-video run.

## Week 4 — Evaluate and improve the system

**What you learned:** define expected behavior, test normal and difficult cases, compare against a baseline, inspect failures, and measure improvement.

**How RaceTime applies it:** the evidence workflow has 40 synthetic evaluation cases covering time boundaries, missing evidence, conflicts and related edge cases. It passed 40/40 versus 20/40 for naive overlap. Separate tests check accounts, cancellation and restart behavior. The Video workspace's Evaluation tab collects human judgments of supported statements, missed events, spoiler leaks and timestamp errors.

**Why it fits:** there is a repeatable dataset, a comparison and explicit failure reporting. Local activity trails and usage records help explain behavior.

**Show it:** use the Evidence demo's Capstone learning tab for the evaluation report, then show the real-review form in Video workspace. These scores measure synthetic evidence rules, not real-video accuracy. Full Week 4 evidence still needs reviewed race cases, verified LangSmith case/model/tool traces, and measured before/after results for targeted improvements. LangSmith is currently blocked by trace quota.

## Week 5 — Specialize a small model with LoRA

**What you learned:** prepare labelled examples, train a small adapter while base weights stay frozen, evaluate on held-out data, merge the adapter and test inference.

**How RaceTime applies it:** the separate BERT-tiny experiment classifies race questions as recap, runner, verify or compare. It uses PyTorch, Transformers and PEFT. Both comparison arms train a classifier head; the LoRA arm also trains adapters. On 144 training and 40 held-out authored examples, accuracy rose from 52.5% to 70%—a 17.5 percentage-point improvement. The report includes class-level scores and a confusion matrix; merged inference was checked.

**Why it fits:** this demonstrates specialization and honest comparison in your race domain. It adapts the technique using an encoder classifier, not the handout's Qwen3/LLaMA Factory generative-model workflow. The handout permits custom exploration, but this is not an exact replication of that exercise.

**Show it:** open LoRA routing evaluation in the Evidence demo's Capstone learning tab and explain both the improvement and the 12 remaining errors out of 40. The trained router is not deployed; it does not watch video or produce the recap. No real-user quality, speed or cost advantage has been established.

## A simple explanation for your capstone presentation

> “Week 1 helped me build the race-viewing app. Week 2 helped it answer from timestamped evidence. Week 3 added controlled decisions and recoverable human review. Week 4 added evaluation and failure analysis. Week 5 let me test a small specialized router. I separate the results I have measured from the real-race validation still to do.”
