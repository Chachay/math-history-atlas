from scripts.common import ROOT, load_yaml_files
from scripts.semantic_network import build_concept_evolution


def projection():
    return build_concept_evolution(
        load_yaml_files(ROOT/'data/entities'),
        load_yaml_files(ROOT/'data/questions'),
        load_yaml_files(ROOT/'data/concept_states'),
        load_yaml_files(ROOT/'data/assertions'),
    )


def test_concept_evolution_groups_states_by_identity_without_inventing_edges():
    out=projection()
    assert out['projection_version']==3
    for concept in out['concepts']:
        years=[s.get('period',{}).get('from',999999) for s in concept['states']]
        assert years==sorted(years)
        assert 'does not imply' in concept['ordering_note']
        for transition in concept['evidence_transitions']:
            assert transition['claim_id'] in concept['related_claim_ids']


def test_function_concept_exposes_multiple_attested_states_when_available():
    out=projection()
    function=next((c for c in out['concepts'] if c['concept_id']=='concept-function'),None)
    assert function is not None
    assert len(function['states']) >= 2


def test_build_emits_concept_evolution_projection():
    source=(ROOT/'scripts/build.py').read_text(encoding='utf-8')
    assert "concept-evolution.json" in source
    assert "build_concept_evolution" in source


def test_ui_query_layer_preserves_graph_and_navigation_separation():
    source=(ROOT/'app/src/lib/graphQueries.ts').read_text(encoding='utf-8')
    assert 'getNeighbors' in source
    assert 'getConceptStates' in source
    assert 'getConceptEvolution' in source
    assert 'groupAdjacentEdges' in source
    assert 'READER_RELATION_GROUPS' in source
