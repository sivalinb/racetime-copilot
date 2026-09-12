"""Generate editable README diagrams from the implemented Copilot workflow.

SVG assets have no external resources, scripts, personal photographs or fonts.
Render the SVGs to PNG when updating the README previews.
"""

from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "architecture"
INK, MUTED = "#203646", "#526976"
TEAL, BLUE, AMBER = "#187b70", "#396f9a", "#a66b27"


class Diagram:
    """Small SVG authoring surface with explicit geometry and accessible labels."""

    def __init__(self, title: str, description: str, height: int):
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="{height}" viewBox="0 0 1440 {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
            f'<rect width="1440" height="{height}" rx="24" fill="#f5f3eb"/>',
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10Z" fill="#6a8790"/></marker></defs>',
        ]

    def rect(self, x, y, w, h, fill="#ffffff", radius=18, stroke="none"):
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'
        )

    def text(self, x, y, value, size=24, color=INK, weight=400):
        self.parts.append(
            f'<text x="{x}" y="{y}" font-family="DejaVu Sans, sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(value)}</text>'
        )

    def path(self, value, stroke=TEAL, width=3, fill="none", arrow=False):
        marker = ' marker-end="url(#arrow)"' if arrow else ""
        self.parts.append(
            f'<path d="{value}" stroke="{stroke}" stroke-width="{width}" fill="{fill}" stroke-linecap="round" stroke-linejoin="round"{marker}/>'
        )

    def circle(self, x, y, radius, fill, stroke="none", width=2):
        self.parts.append(
            f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'
        )

    def label(self, x, y, number, text):
        self.circle(x + 18, y - 8, 18, TEAL)
        self.text(x + 11, y, str(number), 21, "#ffffff", 700)
        self.text(x + 50, y, text, 26, INK, 700)

    def save(self, name: str):
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / name).write_text("\n".join(self.parts + ["</svg>"]), encoding="utf-8")


def introduction() -> None:
    """Illustrate the fan's missed interval and evidence-based catch-up experience."""
    d = Diagram(
        "RaceTime Copilot at a glance",
        "A long race broadcast continues while a fan steps away. The fan chooses an available interval and spoiler cutoff, then reviews a recap with timestamped evidence. Screens are illustrative.",
        670,
    )
    d.text(40, 48, "RACETIME COPILOT  /  THE PRODUCT", 18, TEAL, 700)
    d.text(40, 104, "The race keeps going. Catch up when you can.", 38, INK, 700)
    d.text(
        40,
        145,
        "For race fans, crews and organizers who need the story behind a missed interval.",
        23,
        MUTED,
    )
    for x in [40, 520, 1000]:
        d.rect(x, 185, 400, 370)
    d.path("M458 364 H500", "#6a8790", arrow=True)
    d.path("M938 364 H980", "#6a8790", arrow=True)
    d.label(62, 230, 1, "Step away")
    d.label(542, 230, 2, "Choose an interval")
    d.label(1022, 230, 3, "Review the recap")
    # A broadcast screen, mountain course and an elapsed-time clock.
    d.rect(70, 262, 340, 190, "#dceaf0", 12)
    d.path("M75 406 L149 307 L213 374 L283 289 L405 419 Z", "none", 0, "#83afa9")
    d.path("M75 428 L154 354 L209 411 L301 344 L405 428 Z", "none", 0, "#386c72")
    d.path("M129 439 C265 436 189 395 302 369", "#f7df9b", 5)
    d.circle(118, 299, 16, "#efc879")
    d.rect(267, 274, 128, 32, "#203646", 9)
    d.text(280, 298, "24h+ races", 19, "#ffffff", 700)
    d.circle(355, 417, 33, "#ffffff", TEAL, 3)
    d.path("M355 394 V417 L369 428", TEAL, 3)
    d.text(70, 490, "Sleep, work, life.", 25, INK, 700)
    d.text(70, 527, "The broadcast carries on.", 22, MUTED)
    # A deliberately generic interval selection interface.
    d.rect(550, 262, 340, 190, "#eaf0f5", 12)
    d.text(568, 298, "YouTube link or video", 23, BLUE, 700)
    d.rect(568, 317, 303, 45, "#ffffff", 8)
    d.text(585, 347, "10:00 → 15:00", 26, INK, 700)
    d.path("M575 394 H865", "#becbd2", 7)
    d.path("M643 394 H727", TEAL, 8)
    d.circle(643, 394, 9, TEAL)
    d.circle(727, 394, 9, TEAL)
    d.path("M745 379 V409", AMBER, 3)
    d.text(568, 437, "Spoiler cutoff  15:00", 21, AMBER, 700)
    d.text(550, 490, "Ask what you missed.", 25, INK, 700)
    d.text(550, 527, "Set the time boundaries.", 22, MUTED)
    # Evidence cards, not a claim of actual race outcomes.
    d.rect(1030, 262, 340, 190, "#e6f1ea", 12)
    for y, stamp in [(282, "12:40"), (355, "14:10")]:
        d.rect(1047, y, 305, 60, "#ffffff", 8)
        d.path(f"M1063 {y + 17} L1077 {y + 30} L1063 {y + 43} Z", TEAL, 1, TEAL)
        d.text(1090, y + 27, stamp + "  ·  Evidence", 20, TEAL, 700)
        d.text(1090, y + 48, "Open the source moment", 16, MUTED)
    d.text(1030, 490, "Read. Watch. Decide.", 25, INK, 700)
    d.text(1030, 527, "Approve or reject after review.", 21, MUTED)
    d.text(40, 602, "Recap + timestamps + visible gaps + human review", 28, TEAL, 700)
    d.text(
        40,
        640,
        "Illustrative screens. Live questions require captured coverage; uncaptured past footage is unavailable.",
        20,
        MUTED,
    )
    d.save("racetime-readme-intro.svg")


def architecture() -> None:
    """Show the Python video workspace and distinguish its supporting labs."""
    d = Diagram(
        "RaceTime Copilot architecture overview",
        "Video sources enter a Streamlit account-scoped job queue. A worker runs a bounded LangGraph agent that retrieves evidence, optionally inspects video with Gemini and generates a checked recap. SQLite persists jobs, observations and review checkpoints. Local traces and optional LangSmith support inspection; the TypeScript evidence demo and LoRA training lab are separate.",
        1150,
    )
    d.text(40, 48, "RACETIME COPILOT  /  IMPLEMENTED VIDEO WORKSPACE", 18, TEAL, 700)
    d.text(40, 101, "From a race question to evidence you can review", 36, INK, 700)
    d.text(
        40,
        141,
        "Python application • bounded model calls • persistent jobs and human review",
        23,
        MUTED,
    )
    for x, w in [(40, 400), (520, 400), (1000, 400)]:
        d.rect(x, 190, w, 180)
    d.label(62, 232, 1, "Video sources")
    d.text(64, 277, "Public YouTube or upload", 23)
    d.text(64, 312, "Live: yt-dlp + FFmpeg", 22, BLUE)
    d.text(64, 345, "Completed segments only", 20, MUTED)
    d.label(542, 232, 2, "Streamlit + service")
    d.text(544, 277, "Sign in · question · interval", 23)
    d.text(544, 312, "Validate time and cutoff", 22, BLUE)
    d.text(544, 345, "Save an owner-scoped job", 20, MUTED)
    d.label(1022, 232, 3, "Background worker")
    d.text(1024, 277, "Claim queued work", 23)
    d.text(1024, 312, "Leases, budgets, cancellation", 21, BLUE)
    d.text(1024, 345, "Run or resume investigation", 20, MUTED)
    d.path("M458 282 H500", "#6a8790", arrow=True)
    d.path("M938 282 H980", "#6a8790", arrow=True)
    d.path("M1200 370 V398 H484 V430", "#6a8790", arrow=True)
    # Agent and model boundary.
    d.rect(40, 440, 880, 335, "#e4edf3")
    d.text(65, 482, "BOUNDED LANGGRAPH AGENT", 25, BLUE, 700)
    for x, title, first, second in [
        (65, "Retrieve", "Eligible observations", "Semantic ranking"),
        (350, "Plan", "Permitted actions", "Bounded iterations"),
        (635, "Act", "Inspect or summarize", "Clarify if insufficient"),
    ]:
        d.rect(x, 510, 255, 135)
        d.text(x + 16, 545, title, 26, BLUE, 700)
        d.text(x + 16, 583, first, 19)
        d.text(x + 16, 615, second, 19, MUTED)
    d.path("M323 575 H342", "#6a8790", 2, arrow=True)
    d.path("M608 575 H627", "#6a8790", 2, arrow=True)
    d.text(
        65, 689, "Inspect → retrieve again  ·  Planner enforces action limits", 22, BLUE
    )
    d.rect(65, 709, 825, 46, "#ffffff", 10)
    d.text(
        82, 740, "Cited recap → grounding check → durable review pause", 23, TEAL, 700
    )
    d.rect(1000, 440, 400, 335, "#fbefd9")
    d.circle(1050, 478, 15, "#d9a254")
    d.text(1078, 486, "GEMINI API", 27, AMBER, 700)
    for y, line in [
        (537, "Video inspection"),
        (577, "Embeddings and planning"),
        (617, "Recap and grounding"),
    ]:
        d.text(1025, y, line, 23)
    d.text(1025, 676, "Model output can be wrong.", 21, AMBER, 700)
    d.text(1025, 713, "Failed generation falls back", 20, MUTED)
    d.text(1025, 744, "to labelled evidence extracts.", 20, MUTED)
    d.path("M922 562 H997", "#6a8790", arrow=True)
    d.path("M997 606 H922", "#6a8790", arrow=True)
    # Persistence, review, and observability are intentionally distinct.
    for x in [40, 520, 1000]:
        d.rect(x, 840, 400, 183, "#ffffff")
    d.path("M240 775 V835", "#6a8790", arrow=True)
    d.path("M720 775 V835", "#6a8790", arrow=True)
    d.text(64, 882, "SQLite persistence", 26, BLUE, 700)
    d.text(64, 923, "Accounts, jobs, observations", 22)
    d.text(64, 958, "Usage and graph checkpoints", 22)
    d.text(64, 994, "Local files under .runtime/", 20, MUTED)
    d.text(544, 882, "Human review", 26, TEAL, 700)
    d.text(544, 923, "Recap + timestamps + gaps", 22)
    d.text(544, 958, "Approve or reject; save decision", 21)
    d.text(544, 994, "Approval does not certify truth.", 20, MUTED)
    d.text(1024, 882, "Observability", 26, BLUE, 700)
    d.text(1024, 923, "Local traces and usage", 22)
    d.text(1024, 958, "Optional LangSmith export", 22)
    d.text(1024, 994, "Requires account and quota", 20, MUTED)
    d.text(40, 1073, "SEPARATE CAPSTONE COMPONENTS", 18, TEAL, 700)
    d.text(
        40,
        1111,
        "TypeScript evidence demo + D1/LRU   •   Evaluation pack   •   LoRA routing lab (not used by this agent)",
        21,
        MUTED,
    )
    d.save("racetime-readme-architecture.svg")


if __name__ == "__main__":
    introduction()
    architecture()
