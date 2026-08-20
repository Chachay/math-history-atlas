import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collections import defaultdict
from scripts.common import ROOT, load_yaml_files

def build_intersections():
    stories=load_yaml_files(ROOT/'editorial/stories'); refs=defaultdict(list)
    for s in stories:
        for step in s.get('steps',[]): refs[step['ref']].append(s['id'])
    return [{'entity':k,'story_count':len(set(v)),'stories':sorted(set(v))} for k,v in sorted(refs.items()) if len(set(v))>1]
