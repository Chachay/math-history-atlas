from scripts.validate import validate_all
from scripts.build_intersections import build_intersections
from scripts.common import ROOT, load_yaml_files
from scripts.integrity import artifact_integrity, require_integrity_match, validate_finding_ids


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


def test_integrity_fingerprint_rejects_stale_resolution():
    packet = {'research_unit': {'id': 'R999'}, 'assertions': [{'id': 'a1'}]}
    review = {
        'review': {'research_unit_id': 'R999'},
        'findings': [{'id': 'f1', 'classification': 'PASS'}],
    }
    validate_finding_ids(review)
    stored = artifact_integrity(packet, review)
    require_integrity_match(stored, packet, review, artifact_name='resolution')

    changed_packet = {'research_unit': {'id': 'R999'}, 'assertions': [{'id': 'a1'}, {'id': 'a2'}]}
    try:
        require_integrity_match(stored, changed_packet, review, artifact_name='resolution')
    except RuntimeError as exc:
        assert 'stale' in str(exc)
    else:
        raise AssertionError('stale packet should be rejected')


def test_integrity_requires_stable_unique_finding_ids():
    review = {'findings': [{'id': 'f1'}, {'id': 'f1'}]}
    try:
        validate_finding_ids(review)
    except ValueError as exc:
        assert 'Duplicate' in str(exc)
    else:
        raise AssertionError('duplicate finding IDs should be rejected')
