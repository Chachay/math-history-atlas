import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.common import ROOT, load_yaml_files

def build_person_index():
    entities=load_yaml_files(ROOT/'data/entities'); assertions=load_yaml_files(ROOT/'data/assertions'); stories=load_yaml_files(ROOT/'editorial/stories')
    out=[]
    for p in [e for e in entities if e.get('type')=='Person']:
        related=[a for a in assertions if a.get('subject')==p['id'] or a.get('object')==p['id']]
        story_ids=[]
        for s in stories:
            if any(st.get('ref')==p['id'] for st in s.get('steps',[])): story_ids.append(s['id'])
        out.append({'person':p['id'],'name':p['name'],'assertions':[a['id'] for a in related],'stories':story_ids})
    return out
