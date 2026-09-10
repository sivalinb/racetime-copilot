"""One command starts Streamlit and, if needed, the shared local backend."""
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
import requests

ROOT = Path(__file__).resolve().parents[1]
BASE = 'http://localhost:3000'


def backend_ready():
    try:
        session = requests.Session()
        session.trust_env = False
        data = session.get(BASE + '/api/workspace', timeout=2).json()
        return data.get('capabilities', {}).get('mode') == 'extractive' and any(s.get('id') == 'demo' for s in data.get('sources', []))
    except (requests.RequestException, ValueError):
        return False


def occupied(port):
    for family, kind, proto, _, address in socket.getaddrinfo('localhost', port, type=socket.SOCK_STREAM):
        with socket.socket(family, kind, proto) as sock:
            sock.settimeout(1)
            if sock.connect_ex(address) == 0:
                return True
    return False


def main():
    owned_backend = None
    frontend = None
    os.chdir(ROOT)
    if occupied(8501):
        raise SystemExit('Port 8501 is already in use. Stop the existing Streamlit demo first.')
    try:
        if not backend_ready():
            if occupied(3000):
                raise SystemExit('Port 3000 belongs to another service. Free it before starting this demo.')
            npm = shutil.which('npm')
            if not npm or not (ROOT / 'node_modules').exists():
                raise SystemExit('Install Node.js 22.13+, then run npm ci in this project.')
            owned_backend = subprocess.Popen([npm, 'run', 'dev', '--', '--host', '127.0.0.1'], cwd=ROOT)
            deadline = time.monotonic() + 60
            while not backend_ready():
                if owned_backend.poll() is not None or time.monotonic() > deadline:
                    raise SystemExit('Backend did not start. Inspect its output above.')
                time.sleep(0.5)
        env = {**os.environ, 'RACETIME_API_URL': BASE}
        print('RaceTime Streamlit demo: http://localhost:8501', flush=True)
        frontend = subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py', '--server.address', '127.0.0.1', '--server.port', '8501', '--server.headless', 'true', '--browser.gatherUsageStats', 'false'], cwd=ROOT, env=env)
        frontend.wait()
    except KeyboardInterrupt:
        pass
    finally:
        for process in [frontend, owned_backend]:
            if process is not None and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    process.kill()


if __name__ == '__main__':
    main()
