"""Session-scoped client for the same validated backend used by the web app."""
import os
import re
from urllib.parse import urlparse
import requests


def elapsed(value: str) -> int:
    value = value.strip()
    if not re.fullmatch(r'\d+(?::[0-5]\d){0,2}', value):
        raise ValueError('Use seconds, MM:SS, or HH:MM:SS.')
    result = 0
    for part in value.split(':'):
        result = result * 60 + int(part)
    return result


def clock(seconds: float) -> str:
    seconds = max(0, int(seconds))
    return f'{seconds // 3600:02}:{seconds // 60 % 60:02}:{seconds % 60:02}'


class RaceTimeClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or os.environ.get('RACETIME_API_URL', 'http://localhost:3000')).rstrip('/')
        url = urlparse(self.base_url)
        if url.scheme != 'http' or url.hostname not in {'127.0.0.1', 'localhost', '::1'}:
            raise ValueError('The local demo expects a loopback HTTP backend URL.')
        self.session = requests.Session()
        self.session.trust_env = False

    def call(self, path: str, body: dict | None = None) -> dict:
        try:
            result = self.session.request('POST' if body is not None else 'GET', f'{self.base_url}/api/{path}', json=body, timeout=30)
        except requests.RequestException as exc:
            raise RuntimeError('The recap backend is unavailable. Start the demo with: python scripts/run_demo.py') from exc
        try:
            data = result.json()
        except ValueError as exc:
            raise RuntimeError('The backend returned an unexpected response. Check its terminal output.') from exc
        if not result.ok:
            raise ValueError(data.get('error', 'The request failed.'))
        return data
