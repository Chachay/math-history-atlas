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
