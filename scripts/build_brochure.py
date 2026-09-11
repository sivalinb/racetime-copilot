"""Build the six-page RaceTime guide, using measured repository reports."""

import json
import sys
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
OUT = (
    Path(sys.argv[1])
    if len(sys.argv) > 1
    else ROOT / "docs/RaceTime-Copilot-Brochure.pdf"
)
OUT.parent.mkdir(parents=True, exist_ok=True)
W, H = 792, 612
INK = "#20263e"
BLUE = "#303aa0"
TEAL = "#087b7b"
MUTED = "#526077"
LINE = "#d8e1ed"
PALE = "#eef2ff"
c = canvas.Canvas(str(OUT), pagesize=(W, H))
c.setTitle("RaceTime Copilot - Product, technology and capstone evidence")
c.setAuthor("Siva Babu")
E = json.loads((ROOT / "reports/workflow-evaluation.json").read_text())
R = json.loads((ROOT / "reports/router-evaluation.json").read_text())
page = 0


def text(txt, x, y, w, size=11, color=INK, bold=False):
    p = Paragraph(
        txt,
        ParagraphStyle(
            "p",
            fontName="Helvetica-Bold" if bold else "Helvetica",
            fontSize=size,
            leading=size * 1.34,
            textColor=HexColor(color),
            spaceAfter=0,
        ),
    )
    _, h = p.wrap(w, 1000)
    p.drawOn(c, x, H - y - h)
    return h


def box(x, y, w, h, color=PALE):
    c.setFillColor(HexColor(color))
    c.roundRect(x, H - y - h, w, h, 10, fill=1, stroke=0)


def start(section, title, subtitle):
    global page
    page += 1
    c.setFillColor(white)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    text("RACETIME / COPILOT", 42, 25, 230, 10, BLUE, True)
    text(
        "Problem     People     Workflow     Learning     Results     Demo",
        325,
        26,
        430,
        8,
        MUTED,
    )
    c.setStrokeColor(HexColor(LINE))
    c.line(42, H - 48, 750, H - 48)
    text(section.upper(), 42, 66, 700, 9, TEAL, True)
    text(title, 42, 86, 708, 27, INK, True)
    text(subtitle, 42, 128, 708, 11, MUTED)


def end():
    c.setStrokeColor(HexColor(LINE))
    c.line(42, 43, 750, 43)
    text(
        "LOCAL CAPSTONE / Video + evidence workspaces / 10 SEP 2026",
        42,
        577,
        510,
        8,
        MUTED,
    )
    text(f"{page:02d} / 6", 700, 577, 55, 8, MUTED, True)
    c.showPage()


def art(name, y=169, h=275):
    path = ROOT / "public/art" / f"{name}.png"
    im = ImageReader(str(path))
    iw, ih = im.getSize()
    scale = min(708 / iw, h / ih)
    ww, hh = iw * scale, ih * scale
    c.drawImage(im, 42 + (708 - ww) / 2, H - y - hh, ww, hh, mask="auto")


def cards(items, y=452, h=96):
    gap = 14
    w = (708 - gap * (len(items) - 1)) / len(items)
    for i, (title, body) in enumerate(items):
        x = 42 + i * (w + gap)
        box(x, y, w, h, "#eef2ff" if i % 2 == 0 else "#e9f5f2")
        text(title, x + 14, y + 12, w - 28, 11, BLUE, True)
        text(body, x + 14, y + 34, w - 28, 10)


def rows(items, y=180, widths=(132, 275, 301), rh=65):
    for i, (a, b, d) in enumerate(items):
        yy = y + i * rh
        box(42, yy, 708, rh - 5, "#f0f3fa" if i % 2 == 0 else "#f7f9fc")
        off = 42
        for j, v in enumerate([a, b, d]):
            text(
                v,
                off + 12,
                yy + 12,
                widths[j] - 24,
                10,
                BLUE if j == 0 else INK,
                j == 0,
            )
            off += widths[j]


start(
    "1 / The problem",
    "Missed 15 minutes? Catch up.",
    "RaceTime Copilot helps you understand a chosen race interval through timestamped evidence.",
)
art("overview", 165, 260)
cards(
    [
        (
            "The problem",
            "Long broadcasts are hard to catch up on. Scrubbing can miss key moments or reveal future results.",
        ),
        (
            "The useful result",
            "Choose a window, follow a runner, and see what the sources reported - including disagreements.",
        ),
        (
            "What works today",
            "Video jobs, learned retrieval and cited recaps. A key-free evidence demo is also included. See validation limits.",
        ),
    ],
    439,
    108,
)
end()

start(
    "2 / Who it helps",
    "For the people following the race.",
    "Built by Siva Babu: ultramarathoner, race organizer and observability practitioner.",
)
art("audience", 166, 260)
cards(
    [
        (
            "Fans and families",
            "Catch up together on a missed interval. Inspect the evidence behind a reported sighting or position.",
        ),
        (
            "Organizers and crews",
            "Review imported commentary and timing context. Keep uncertain reports visible.",
        ),
        (
            "Why this project",
            "A personal race-viewing problem meets systems skills: time boundaries, memory limits and useful traces.",
        ),
    ],
    439,
    108,
)
end()

start(
    "3 / How it works",
    "One question. One evidence workflow.",
    "Save a video, choose an interval and spoiler cutoff, then ask what happened. Review the cited evidence.",
)
art("workflow", 170, 210)
rows(
    [
        (
            "Retrieve",
            "Keep only evidence fully inside the window.",
            "Inspect bounded video windows and rank learned evidence vectors.",
        ),
        (
            "Check",
            "Generate a cited recap and check its grounding.",
            "Exclude later evidence. Say when there is not enough evidence.",
        ),
        (
            "Review",
            "Read the timestamped recap and its trace.",
            "Pause at a durable checkpoint; approve or reject, even after a restart.",
        ),
    ],
    386,
    rh=53,
)
text(
    "A bounded Gemini planner chooses legal actions. Coverage gaps and provider failures remain visible.",
    42,
    552,
    708,
    9,
    MUTED,
)
end()

start(
    "4 / Technology and learning",
    "Each tool has a clear job.",
    "Five course themes applied to one product. The detailed technology map is in docs/technology-map.md.",
)
rows(
    [
        (
            "Week 1 / App",
            "Streamlit, Python and persistent accounts.",
            "Save videos, queue jobs and review results. TypeScript/Zod powers the optional evidence demo.",
        ),
        (
            "Week 2 / Retrieval",
            "Gemini video, learned embeddings and citations.",
            "Inspect a fixed interval, retrieve evidence, generate a recap and check the cited observations.",
        ),
        (
            "Week 3 / Workflow",
            "LangGraph, SQLite jobs and durable review.",
            "Bound model decisions, retry calls and resume review. Weighted LRU remains in the evidence demo.",
        ),
        (
            "Week 4 / Evaluation",
            "Unit tests, AppTest, traces and human labels.",
            "Test restart and time rules. Real-race labels and external trace quota are still required.",
        ),
        (
            "Week 5 / LoRA",
            "PyTorch, Transformers, PEFT and scikit-learn.",
            "Train, evaluate and merge a BERT-tiny adapter. This adapts the technique, not the exact Qwen3/LLaMA Factory setup.",
        ),
    ],
    173,
    rh=73,
)
text(
    "Live capture uses FFmpeg and yt-dlp. Public deployment scaffolding is prepared; the current scope is local.",
    42,
    550,
    708,
    9,
    MUTED,
)
end()

start(
    "5 / Evidence that it works",
    "Small tests. Clear limits.",
    "These measurements use authored synthetic data. They do not establish real-video summary quality.",
)
for i, (value, label) in enumerate(
    [
        ("38 / 38", "17 evidence + 21 product tests"),
        (f"{E['passed']} / {E['count']}", "Evidence cases"),
        ("Passed", "Streamlit + API flows"),
    ]
):
    x = 42 + i * 241
    box(x, 177, 226, 88)
    text(value, x + 16, 192, 194, 26, BLUE, True)
    text(label, x + 16, 233, 194, 10)
rows(
    [
        (
            "Spoiler test",
            "Request 00:00-15:00 of fictional Canyon Relay.",
            "Two ridge reports disagree. The update at 15:30 stays out.",
        ),
        (
            "Evidence result",
            f"Naive baseline {E['baselinePassed']}/40 -> workflow {E['passed']}/40.",
            "Strict time and availability rules explain the measured improvement.",
        ),
        (
            "Separate LoRA lab",
            "52.5% baseline -> 70% held-out accuracy.",
            "144 training / 40 held-out examples. The app keeps the rule router; the trained adapter is not deployed.",
        ),
    ],
    285,
    rh=69,
)
text(
    "Real Gemini check: small uploaded video, embeddings, cited recap and durable review passed.",
    42,
    507,
    708,
    10,
)
text(
    "YouTube and large-file processing remain provider-dependent. Active live capture and race accuracy need validation.",
    42,
    536,
    708,
    10,
    MUTED,
)
end()

start(
    "6 / Run it and extend it",
    "A simple demo. A clear next step.",
    "Video workspace: Python 3.11+ and a Gemini key. The optional evidence demo also needs Node.js 22.13+.",
)
box(42, 175, 340, 190)
text("START LOCALLY", 58, 188, 308, 11, BLUE, True)
commands = [
    "python3 -m venv .venv",
    "source .venv/bin/activate",
    "pip install -r requirements.txt",
    "# configure Gemini in .env",
    "python scripts/run_product.py",
]
for i, line in enumerate(commands):
    text(line, 58, 220 + i * 23, 308, 10)
text("Open http://localhost:8501", 58, 341, 308, 11, TEAL, True)
text("Try this first", 407, 182, 330, 15, BLUE, True)
text(
    "Create a local account. Save a short video and queue a question. Open Jobs / results, check timestamps and approve or reject the recap.",
    407,
    217,
    330,
    12,
)
text(
    "For a key-free fallback, use run_demo.py and the fictional Canyon Relay scenario. Setup steps are in docs/setup.md.",
    407,
    302,
    330,
    10,
    MUTED,
)
rows(
    [
        (
            "Next",
            "Validate real race clips and an active stream.",
            "Review timestamps and claims independently. Resolve provider access and external trace quota.",
        ),
        (
            "Then",
            "Pilot with race fans and organizers.",
            "Measure time saved and evidence accuracy. Explore timing feeds, runner watchlists and multi-camera recaps.",
        ),
    ],
    387,
    rh=62,
)
text("github.com/sivalinb/racetime-copilot", 42, 522, 708, 13, BLUE, True)
c.linkURL(
    "https://github.com/sivalinb/racetime-copilot",
    (42, H - 544, 750, H - 520),
    relative=0,
)
text(
    "Read: README -> docs/learning-guide.md -> docs/demo-guide.md. Course scope: user-provided Week 1-5 handouts.",
    42,
    549,
    708,
    8,
    MUTED,
)
end()
c.save()
print(OUT)
