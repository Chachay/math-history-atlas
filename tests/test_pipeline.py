import subprocess
import sys
import yaml

from scripts.validate import validate_all
from scripts.build_intersections import build_intersections
from scripts.common import ROOT, load_yaml_files
from scripts.integrity import artifact_integrity, require_integrity_match, validate_finding_ids
from scripts.validate_provenance import validate_provenance


def test_sample_data_valid():
    assert validate_all() == []


def test_fourier_is_intersection():
    rows = build_intersections()
    hit = [x for x in rows if x['entity'] == 'concept-fourier-series']
    assert hit and hit[0]['story_count'] == 3


def test_r001_story_has_reviewable_narrative_provenance():
    stories = load_yaml_files(ROOT / 'editorial/stories')
    story = next(s for s in stories if s['id'] == 'story-fourier-heat-representation')
    assert story['steps']
    assert all(step.get('narrative') for step in story['steps'])
    assert all(step.get('assertion_refs') for step in story['steps'])


def test_r002_story_has_reviewable_narrative_provenance():
    stories = load_yaml_files(ROOT / 'editorial/stories')
    story = next(s for s in stories if s['id'] == 'story-cauchy-rigor-continuity')
    assert story['steps']
    assert all(step.get('narrative') for step in story['steps'])
    assert all(step.get('assertion_refs') for step in story['steps'])
    assert all(step.get('perspective') for step in story['steps'])


def test_r005_replaces_duplicate_rigor_story_with_quantified_control_story():
    stories = load_yaml_files(ROOT / 'editorial/stories')
    assert not any(s['id'] == 'story-rigor' for s in stories)
    story = next(s for s in stories if s['id'] == 'story-quantified-control')
    assert story['steps']
    assert all(step.get('narrative') for step in story['steps'])
    assert all(step.get('assertion_refs') for step in story['steps'])
    assert all(step.get('perspective') for step in story['steps'])
    assert all(step.get('temporal_anchor') for step in story['steps'])


def test_story_transitions_resolve_to_reviewed_steps_and_assertions():
    stories = load_yaml_files(ROOT / 'editorial/stories')
    assertions = load_yaml_files(ROOT / 'data/assertions')
    transitions = yaml.safe_load((ROOT / 'editorial/story-transitions.yaml').read_text(encoding='utf-8')) or []
    story_map = {s['id']: s for s in stories}
    assertion_ids = {a['id'] for a in assertions}

    assert transitions
    for transition in transitions:
        source = story_map[transition['from_story']]
        target = story_map[transition['to_story']]
        source_step = next(s for s in source['steps'] if s['id'] == transition['from_step'])
        target_step = next(s for s in target['steps'] if s['id'] == transition['to_step'])
        assert transition['assertion_refs']
        assert set(transition['assertion_refs']) <= assertion_ids
        assert transition['perspective'] in {'historical', 'later_interpretation', 'modern_abstraction'}
        if transition['type'] != 'retrospective':
            assert source_step['temporal_anchor']['from'] <= target_step['temporal_anchor']['from']


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


def test_integrity_cli_modules_are_invokable_from_repo_root():
    for module in ('scripts.bind_resolution', 'scripts.promote_verified'):
        result = subprocess.run(
            [sys.executable, '-m', module, '--help'],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr


def test_canonical_promotion_provenance_maps_are_valid():
    assert validate_provenance() == []
