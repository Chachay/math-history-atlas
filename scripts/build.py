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

def build_question_projection_edges(stories, questions, assertions):
    """Compress each Story path onto its Question nodes for Network projection only.

    These generated edges are not canonical assertions. They preserve the editorial fact
    that two Questions are consecutive along a reviewed Story path even when Work or
    Concept steps lie between them. A canonical Question-to-Question assertion always
    takes precedence over this projection.
    """
    question_ids = {q['id'] for q in questions}
    canonical_pairs = {
        (a.get('subject'), a.get('object'))
        for a in assertions
        if a.get('subject') in question_ids and a.get('object') in question_ids
    }
    projected = {}

    for story in stories:
        steps = {step['id']: step for step in story.get('steps', [])}
        adjacency = {}
        for link in story.get('links', []):
            adjacency.setdefault(link['from'], []).append(link['to'])

        for step_id, step in steps.items():
            source_ref = step.get('ref')
            if source_ref not in question_ids:
                continue

            stack = list(adjacency.get(step_id, []))
            visited = set()
            while stack:
                target_step_id = stack.pop()
                if target_step_id in visited:
                    continue
                visited.add(target_step_id)
                target_step = steps.get(target_step_id)
                if not target_step:
                    continue
                target_ref = target_step.get('ref')

                if target_ref in question_ids:
                    pair = (source_ref, target_ref)
                    if source_ref != target_ref and pair not in canonical_pairs:
                        record = projected.setdefault(pair, {
                            'id': f"projection-{source_ref}-to-{target_ref}",
                            'subject': source_ref,
                            'predicate': 'story_path',
                            'object': target_ref,
                            'perspective': 'editorial_projection',
                            'certainty': 'not_applicable',
                            'status': 'editorial_projection',
                            'projection_stories': [],
                        })
                        if story['id'] not in record['projection_stories']:
                            record['projection_stories'].append(story['id'])
                    continue

                stack.extend(adjacency.get(target_step_id, []))

    return list(projected.values())

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
    projection_edges = build_question_projection_edges(stories, questions, assertions)
    graph_assertions = assertions + projection_edges
    dump('graph.json', {'entities': entities, 'questions': questions, 'assertions': graph_assertions})
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
    print(f'Build completed. Generated JSON synced to app/public/data. Network projection edges: {len(projection_edges)}')

if __name__ == '__main__':
    main()
