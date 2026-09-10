# Architecture illustration prompt

Generated with the built-in image-generation tool on 10 September 2026.

Use case: infographic-diagram.
Asset type: high-resolution landscape illustrated technical architecture for RaceTime Copilot GitHub README and Streamlit.
Create an original hand-drawn engineering infographic: fine navy pen hatching, warm white paper, softly watercolor-tinted blue, purple, amber and teal components, crisp exceptionally legible printed labels mixed with a hand-lettered headline. Similar in spirit to a detailed illustrated field notebook explaining software. Real drawings, not just rectangular text boxes. 16:9 wide composition with ample margins and readable labels. Trail-running mountain ridgeline along top; small runners, race camera, video monitor, server stack, circuit board, database cylinders, magnifying glass, checklist and a small friendly running robot guide at far right. Do not use real faces or reproduce another project's mascot.
Headline exact: "RaceTime Copilot — How a Race Question Runs"
Subtitle exact: "Choose a time range. Retrieve the evidence. Inspect when needed. Review the recap."
Four numbered columns joined by prominent purple arrows, each has a large rich pen illustration and 3 compact labeled cards. Technical accuracy is essential. Keep all text below verbatim; no invented numbers or claims.

Column1 "1  INPUT & QUEUE"
Illustration: laptop showing a race video, playback timeline with selected amber interval, a camera and little queue/server.
Cards:
"YouTube link or video" / "Question + start / end / spoiler cutoff"
"Streamlit + Python worker" / "Account-scoped jobs run in the background"
"SQLite job queue" / "Leases • heartbeat • bounded retries"

Column2 "2  CONSTRAINED AGENT"
Illustration: circuit-board brain, branching trail sign with three arrows, linked state-machine nodes.
Cards:
"LangGraph shared state" / "Retrieve → choose → act → repeat"
"Rules define legal actions" / "inspect • summarize • clarify"
"Gemini chooses when needed" / "Validated action; rule fallback on failure"

Column3 "3  EVIDENCE & CHECKS"
Illustration: video filmstrip with runner frames, magnifying glass, 3D database cylinders connected to embedding dots.
Cards:
"Gemini video inspection" / "Bounded clips → timestamped observations"
"Semantic retrieval" / "768-d embeddings + SQLite + time filters"
"Cited summary + grounding" / "Check cited evidence; show gaps and conflicts"

Column4 "4  HUMAN REVIEW"
Illustration: viewer inspecting recap document beside video, timestamp citation tags, checklist and checkpoint disk.
Cards:
"Recap with evidence" / "Timestamps • coverage gaps • source links"
"Durable LangGraph pause" / "SqliteSaver checkpoint • resume after restart"
"Approve or reject" / "Records your decision; export result + trace"

At far right small running robot speech bubble: "Ask any available interval. Check what the evidence supports."
Below columns one slim full-width illustrated technical foundation band divided into three clearly labelled compartments:
"LOCAL PRODUCT" / "Streamlit • Python • LangGraph • Gemini • SQLite"
"SEPARATE CAPSTONE LABS" / "TypeScript / Zod • D1 • weighted LRU • evaluations • LoRA"
"OBSERVABILITY" / "Local traces • LangSmith when quota is available"
Bottom small but legible boundary strip: "Validation: small-video path verified. YouTube / Files processing blocked in tests. Active livestream test pending."
Final fine print: "Illustrated overview — detailed engineering plates document limits and failure paths."
All content must fit cleanly. Prioritize drawings and hierarchy, avoid microscopic paragraphs. No extra logos or claims of autonomous approval, external vector databases, live testing success, or multi-agent teams.

