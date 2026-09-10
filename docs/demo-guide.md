# Five-minute demo

Follow the README setup, run `python scripts/run_demo.py`, and open **http://localhost:8501**. Use the Streamlit tabs: Recap, Import / live append, History & traces, and Capstone learning.

1. **Problem (30 sec):** "I follow long races. If I miss a few minutes, I want the story for that interval without future spoilers."
2. **Catch-up (60 sec):** Select the fictional demo, `00:00`–`15:00`, cutoff `15:00`, "What happened?". Show E05/E06 disagree and E09 is absent.
3. **Evidence (45 sec):** Explain that these are fictional fixture observations. A YouTube URL on an imported source adds timestamp playback links; URL-only video understanding is deferred.
4. **Operations (45 sec):** Enable one simulated retrieval failure and run. Inspect retry/verification traces. Repeat the same request to show the cache. Approve or reject and inspect history.
5. **Live update (60 sec):** Import the JSON below as a live source with duration `30:00`, available start `00:00`, end `15:00`. Append a new ID later with a larger coverage end. New recaps use the next revision.
6. **Measured learning (60 sec):** Show 40-case evaluation and LoRA results. Explain the small synthetic dataset and why 70% held-out router accuracy does not justify deploying that classifier.

## Minimal JSON import

```json
[
  {"id":"obs-1","start":60,"end":75,"text":"Commentary reports a runner at the checkpoint.","kind":"commentary"},
  {"id":"obs-2","start":80,"end":95,"text":"The timing graphic lists bib 42 at the checkpoint.","kind":"visual","runner":"Bib 42"}
]
```

Append with available end `20:00`:

```json
[{"id":"obs-3","start":960,"end":975,"availableAt":990,"text":"A later timing record reports bib 42 at the next checkpoint.","kind":"timing","runner":"Bib 42"}]
```

Use JSON with unique IDs for repeated live appends. VTT/SRT imports generate sequential cue IDs, so another such append can collide unless IDs are explicitly changed through JSON.

All examples are authored, synthetic observations. Import only evidence you are allowed to use. Source coverage and duration must reflect the imported material, not an assumed complete livestream archive.
