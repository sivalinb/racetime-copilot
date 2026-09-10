"""Run the video product only; no Node backend is needed for this workspace."""
import os,signal,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
from dotenv import load_dotenv
load_dotenv(ROOT/'.env')
processes=[]
def stop(*_):
    for p in processes:
        if p.poll() is None:p.terminate()
    for p in processes:
        try:p.wait(timeout=10)
        except subprocess.TimeoutExpired:p.kill()
    raise SystemExit(0)
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
try:
    processes.append(subprocess.Popen([sys.executable,'-m','racetime.worker']))
    processes.append(subprocess.Popen([sys.executable,'-m','streamlit','run','app.py','--server.address','0.0.0.0' if os.getenv('RACETIME_PUBLIC')=='true' else '127.0.0.1','--server.port','8501','--server.headless','true'],env={**os.environ,'RACETIME_VIDEO_ONLY':'true'}))
    while all(p.poll() is None for p in processes):time.sleep(1)
finally:stop()
