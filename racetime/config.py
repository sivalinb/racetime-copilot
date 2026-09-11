import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
DATA = Path(os.environ.get("RACETIME_DATA_DIR", ROOT / ".runtime")).resolve()
DATA.mkdir(parents=True, exist_ok=True, mode=0o700)
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
EMBED_MODEL = os.environ.get("GEMINI_EMBED_MODEL", "gemini-embedding-2")
MAX_CALLS = int(os.environ.get("RACETIME_MAX_CALLS_PER_JOB", "32"))
DAILY_CALLS = int(os.environ.get("RACETIME_DAILY_CALL_LIMIT", "120"))
MAX_UPLOAD = 100 * 1024 * 1024


def configured():
    return bool(os.environ.get("GEMINI_API_KEY"))
