from scripts.common import ROOT, load_yaml_files
from scripts.atlas_projection import build_atlas_projection


def _projection():
    return build_atlas_projection(
        load_yaml_files(ROOT / 'data/entities'),
        load_yaml_files(ROOT / 'data/questions'),
        load_yaml_files(ROOT / 'data/concept_states'),
        load_yaml_files(ROOT / 'data/assertions'),
    )


def test_atlas_projection_bridges_fields_to_concepts_and_states():
    projection = _projection()
    assert projection['projection_version'] == 3
    analysis = next(row for row in projection['fields'] if row['id'] == 'analysis')
    assert analysis['concept_count'] > 0
    assert analysis['concept_state_count'] > 0
    assert 'concept-function' in analysis['concept_ids']


def test_atlas_projection_exposes_function_evolution_context():
    projection = _projection()
    function = next(row for row in projection['concepts'] if row['id'] == 'concept-function')
    assert function['state_count'] >= 1
    assert function['states'] == sorted(
        function['states'],
        key=lambda row: (row['year'] is None, row['year'] or 0, row['id']),
    )
    assert any(function['related'].values())


def test_atlas_projection_does_not_invent_state_transitions():
    projection = _projection()
    assert all('transitions' not in concept for concept in projection['concepts'])
    assert any('does not create new historical claims' in note for note in projection['notes'])


def test_build_emits_atlas_projection():
    source = (ROOT / 'scripts' / 'build.py').read_text(encoding='utf-8')
    assert "dump('atlas-projection.json'" in source
    assert 'build_atlas_projection' in source
