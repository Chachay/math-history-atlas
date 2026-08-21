import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
import shutil
import yaml
from scripts.common import ROOT, load_yaml_files
from scripts.validate import validate_all
from scripts.build_intersections import build_intersections
from scripts.build_person_index import build_person_index
from scripts.build_atlas import build_atlas

GENERATED = ROOT / 'generated'
APP_DATA = ROOT / 'app' / 'public' / 'data'

def dump(name, obj):
    GENERATED.mkdir(parents=True, exist_ok=True)
    (GENERATED / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def sync_app_data():
    APP_DATA.mkdir(parents=True, exist_ok=True)
    for src in GENERATED.glob('*.json'):
        shutil.copy2(src, APP_DATA / src.name)

def main():
    errs = validate_all()
    if errs:
        raise SystemExit('\n'.join(errs))
    entities = load_yaml_files(ROOT/'data/entities')
    questions = load_yaml_files(ROOT/'data/questions')
    assertions = load_yaml_files(ROOT/'data/assertions')
    stories = load_yaml_files(ROOT/'editorial/stories')
    transition_file = ROOT/'editorial/story-transitions.yaml'
    transitions = yaml.safe_load(transition_file.read_text(encoding='utf-8')) or []
    dump('graph.json', {'entities': entities, 'questions': questions, 'assertions': assertions})
    dump('intersections.json', build_intersections())
    dump('person-index.json', build_person_index())
    dump('story-index.json', [
        {
            'id': s['id'],
            'title': s['title'],
            'fields': s.get('fields', []),
            'steps': s['steps'],
            'links': s['links'],
        }
        for s in stories
    ])
    dump('story-transitions.json', transitions)
    dump('atlas.json', build_atlas())
    sync_app_data()
    print('Build completed. Generated JSON synced to app/public/data.')

if __name__ == '__main__':
    main()
