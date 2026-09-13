# Nebius evaluation and Braintrust observability

Gemini continues to inspect video and generate the recap. Nebius is an optional second-model judge of a response against supplied reference facts. Braintrust is an optional hosted trace destination. They have different jobs.

## Use Nebius in Streamlit

1. Complete a recap and open **Video workspace → Evaluation**.
2. Watch the source and enter timestamped reference facts, answerability and source rationale. If no answer is available, leave facts empty and explain why.
3. Record the actual response type separately. Complete the human review fields; check the blind-label box only if you prepared the labels before seeing the response.
4. Choose **Evaluate with Nebius**. One bounded request scores factual support, completeness, response appropriateness and time-boundary compliance.
5. Inspect the verdict and reasons, download it and follow its trace link when tracing is configured. Human annotations and judge outputs are saved separately under ignored `.runtime/` folders.

The judge uses `Qwen/Qwen3-235B-A22B-Instruct-2507`, verified available in the configured account. It does not receive a hidden expected verdict, API keys or raw video. It sees the question, interval, supplied reference facts and candidate answer. Changing the model is an explicit `NEBIUS_JUDGE_MODEL` setting. Each request has a token cap and timeout; truncated, invalid and failed responses receive no score.

A different model is not independent truth. Incorrect reference facts can still yield misleading evaluations. Calibrate the judge against independent source reviewers before using it for release decisions. It never automatically approves a recap or deployment.

## Measured fixture result

[Actual Nebius report](../evals-observability/benchmarks/nebius-judge-smoke-recorded.json): five real provider requests, 4/5 agreement with authored fixture expectations, zero false acceptances and one false rejection under those expectations. The partial-answer disagreement is retained. This is an integration smoke test, not a real-video accuracy or calibrated-judge claim.

```bash
python scripts/evaluate_nebius.py --input evals-observability/datasets/nebius-judge-smoke-v1.json
```

The default limit is five cases. Reports use unique timestamped paths; existing output paths cannot be overwritten. For reviewed datasets, use the same structure with genuine reviewer verdicts. The expected `human_accept` value is withheld from the model.

## Configure Braintrust

In the ignored `.env`:

```dotenv
NEBIUS_API_KEY=your-local-key
RACETIME_OBSERVABILITY=braintrust
BRAINTRUST_API_KEY=your-local-key
BRAINTRUST_PROJECT=racetime-copilot
BRAINTRUST_PROJECT_ID=your-project-id
```

`BRAINTRUST_PROJECT_ID` overrides the project name. The supplied ID appears as **My Project** in Braintrust; setting `BRAINTRUST_PROJECT=racetime-copilot` does not rename it.

Restart Streamlit and the worker after changing configuration. `RACETIME_OBSERVABILITY` selects one hosted destination: `braintrust`, `langsmith` or `none`. Native LangSmith tracing is disabled at startup when another destination is selected. Existing local result traces remain available.

Braintrust spans explicitly record job, planner, retrieval, inspection, summary/verification, Gemini generation/embedding and Nebius evaluation. The Week 5 local classifier has its own demo span. Model usage metrics, errors, allowed inputs and outputs are recorded; API keys and raw media bytes are excluded. Telemetry failures do not turn a failed provider call into a success or stop a valid application result.

A trace link can be constructed before delivery. It does not prove ingestion. Hosted parent/retrieval/Nebius spans are now verified by server-side readback. [Recorded proof](../evals-observability/observability/examples/braintrust-nebius-check.json) includes 294 input and 159 output tokens for the real judge request. [Open the verified trace](https://www.braintrust.dev/app/siva-project/object?object_type=project_logs&object_id=f1a828a0-8dd9-4519-9839-49740bc5523e&id=0eae6d55-ec00-46a5-a3e4-51e0f280363d). The completed five-minute Safari recording now demonstrates the hosted dashboard, the fresh video trace and this earlier judge fixture. [Demo evidence and local artifact details](../reports/safari-demo.md).

## Recording walkthrough

Show Streamlit's saved video result and citation boundaries; run the Nebius evaluation; inspect the corresponding Braintrust model span and usage; show Nebius's inference activity without displaying credentials; finish with Week 5's actual curve, five examples, held-out errors and live local classification. Use real UI and recorded provider results; do not present fixture footage or a storyboard as a live video analysis.

Sources: [Nebius structured output](https://docs.tokenfactory.nebius.com/ai-models-inference/json), [Braintrust tracing](https://www.braintrust.dev/docs/instrument/advanced-tracing).

Verify a fresh trace with `python scripts/check_braintrust.py --with-nebius` (one real judge call), or omit the flag for a telemetry-only fixture. The checker reads the expected parent and child spans from Braintrust before reporting success.
