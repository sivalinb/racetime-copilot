"""Consistent SQLite backups. Store the output outside the application disk."""
import argparse,sqlite3,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from racetime.config import DATA
p=argparse.ArgumentParser();p.add_argument('destination',type=Path);args=p.parse_args();args.destination.mkdir(parents=True,exist_ok=True)
for name in ['product.sqlite','checkpoints.sqlite']:
    if (DATA/name).exists():
        with sqlite3.connect(DATA/name) as src,sqlite3.connect(args.destination/name) as dst:src.backup(dst)
print('Database backup complete. Also back up uploads/ and evaluations/ to preserve source media and human labels.')
