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
from scripts.semantic_network import (
    build_inquiry_graph,
    build_research_claims,
    build_semantic_network,
    semantic_audit,
)

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
    concept_states = load_yaml_files(ROOT/'data/concept_states')
    stories = load_yaml_files(ROOT/'editorial/stories')
    transition_file = ROOT/'editorial/story-transitions.yaml'
    transitions = yaml.safe_load(transition_file.read_text(encoding='utf-8')) or []

    # Legacy aggregate kept temporarily so the current UI and research tooling do not
    # silently change semantics during the V2 migration. New UI work should consume
    # semantic-network.json / inquiry-graph.json instead.
    dump('graph.json', {'entities': entities, 'questions': questions, 'assertions': assertions})

    dump('semantic-network.json', build_semantic_network(entities, questions, concept_states, assertions))
    dump('inquiry-graph.json', build_inquiry_graph(entities, questions, concept_states, assertions))
    dump('research-claims.json', build_research_claims(entities, questions, concept_states, assertions))
    dump('semantic-audit.json', semantic_audit(entities, questions, concept_states, assertions))

    dump('intersections.json', build_intersections())
    dump('person-index.json', build_person_index())
    dump('story-index.json', [
        {
            'id': s['id'],
            'title': s['title'],
            'description': s.get('description', ''),
            'fields': s.get('fields', []),
            'steps': s['steps'],
            'links': s['links'],
        }
        for s in stories
    ])
    dump('story-transitions.json', transitions)
    dump('atlas.json', build_atlas())
    sync_app_data()
    print('Build completed. Semantic V2 projections and legacy JSON synced to app/public/data.')

if __name__ == '__main__':
    main()
