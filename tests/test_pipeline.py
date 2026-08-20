import yaml

from scripts.validate import validate_all
from scripts.build_intersections import build_intersections
from scripts.common import ROOT, load_yaml_files


def test_sample_data_valid():
    assert validate_all() == []


def test_fourier_is_intersection():
    rows = build_intersections()
    hit = [x for x in rows if x['entity'] == 'concept-fourier-series']
    assert hit and hit[0]['story_count'] == 4


def test_r001_story_has_reviewable_narrative_provenance():
    stories = load_yaml_files(ROOT / 'editorial/stories')
    story = next(s for s in stories if s['id'] == 'story-fourier-heat-representation')
    assert story['steps']
    assert all(step.get('narrative') for step in story['steps'])
    assert all(step.get('assertion_refs') for step in story['steps'])


def test_canonical_provenance_maps_resolve():
    canonical_assertions = {a['id'] for a in load_yaml_files(ROOT / 'data/assertions')}
    stories = {s['id']: s for s in load_yaml_files(ROOT / 'editorial/stories')}

    for path in (ROOT / 'research/promotions').glob('*-canonical-map.yaml'):
        mapping = yaml.safe_load(path.read_text(encoding='utf-8'))
        packet_path = ROOT / mapping['packet']
        packet = yaml.safe_load(packet_path.read_text(encoding='utf-8'))
        packet_assertions = {a['id'] for a in packet.get('assertions', [])}

        for row in mapping.get('canonical_assertions', []):
            assert row['canonical_id'] in canonical_assertions
            for ref in row.get('packet_refs', []):
                if ref.get('section') == 'assertions' and ref.get('id'):
                    assert ref['id'] in packet_assertions

        for mapped_story in mapping.get('stories', []):
            story = stories[mapped_story['story_id']]
            steps = {s['id']: s for s in story['steps']}
            for mapped_step in mapped_story.get('steps', []):
                step = steps[mapped_step['step_id']]
                assert mapped_step['canonical_assertion_refs'] == step.get('assertion_refs', [])
                assert set(mapped_step['canonical_assertion_refs']) <= canonical_assertions


def test_story_reviews_resolve_targets_and_assertions():
    canonical_assertions = {a['id'] for a in load_yaml_files(ROOT / 'data/assertions')}
    stories = {s['id']: s for s in load_yaml_files(ROOT / 'editorial/stories')}

    for path in (ROOT / 'editorial/reviews').glob('*-story-review.yaml'):
        review = yaml.safe_load(path.read_text(encoding='utf-8'))
        story_id = review['review']['story_id']
        assert story_id in stories
        step_ids = {s['id'] for s in stories[story_id]['steps']}

        for finding in review.get('findings', []):
            target = finding.get('target', {})
            assert target.get('story_id') == story_id
            if target.get('step_id'):
                assert target['step_id'] in step_ids
            assert set(finding.get('assertion_refs', [])) <= canonical_assertions
