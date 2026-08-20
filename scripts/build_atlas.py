import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.common import ROOT, load_yaml_files

def build_atlas():
    fields=load_yaml_files(ROOT/'data/fields')
    return {'fields':fields,'note':'Polyhierarchy projection; UI may choose a tree-like view without changing canonical data.'}
