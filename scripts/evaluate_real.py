"""Aggregate actual human annotations; fail instead of inventing an empty benchmark."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from racetime.config import DATA
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=DATA/'evaluations');p.add_argument('--output',type=Path,default=DATA/'real-evaluation.json');args=p.parse_args()
cases=[json.loads(f.read_text()) for f in args.input.rglob('*.json')]
cases=[c for c in cases if c.get('independently_reviewed') and c.get('expected_facts')]
if not cases:raise SystemExit('No independently reviewed real-video cases. Use the Video workspace Evaluation tab first.')
result={'count':len(cases),'mean_supported_percent':sum(c['supported_percent'] for c in cases)/len(cases),'missed_events':sum(c['missed_events'] for c in cases),'spoiler_leaks':sum(c['spoiler_leaks'] for c in cases),'largest_timestamp_error_seconds':max(c['max_timestamp_error_s'] for c in cases),'reviewer_count':len({c['reviewer'] for c in cases}),'source':'human annotations; subjective factual-support judgments, not automatic ground truth'}
args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
