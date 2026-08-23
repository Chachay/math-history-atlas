from scripts.common import ROOT, load_yaml_files
from scripts.semantic_network import build_semantic_network


def network():
    return build_semantic_network(
        load_yaml_files(ROOT / 'data/entities'),
        load_yaml_files(ROOT / 'data/questions'),
        load_yaml_files(ROOT / 'data/concept_states'),
        load_yaml_files(ROOT / 'data/assertions'),
    )


def test_r001_exposes_heat_to_representation_structure():
    graph = network()
    default = set(graph['default_edge_ids'])
    expected = {
        'assertion-r001-v2-fourier-authored-1822',
        'assertion-r001-v2-fourier-addresses-heat-data',
        'assertion-r001-v2-fourier-uses-series-state',
        'assertion-r001-v2-fourier-defines-coefficients',
        'assertion-r001-v2-fourier-uses-arbitrary-function-state',
    }
    assert expected <= default


def test_r002_exposes_1821_to_1853_continuity_structure_without_reifying_the_false_generality():
    graph = network()
    claims = {c['id']: c for c in graph['claims']}
    default = set(graph['default_edge_ids'])
    expected = {
        'assertion-r002-v2-cours-addresses-continuity-sum',
        'assertion-r002-v2-cauchy-1853-revises-cours',
        'assertion-r002-v2-cauchy-1853-addresses-continuity-sum',
        'assertion-r002-v2-cauchy-1853-proves-strengthened',
        'assertion-r002-v2-1853-depends-uniform-condition',
    }
    assert expected <= default
    assert claims['assertion-r002-v2-cauchy-1853-revises-cours']['predicate'] == 'revises'
    assert claims['assertion-r002-v2-1853-depends-uniform-condition']['perspective'] == 'later_interpretation'
    assert 'assertion-r002-v2-cours-proves-continuity-claim' not in claims


def test_r004_exposes_integrability_as_problem_result_and_state():
    graph = network()
    claims = {c['id']: c for c in graph['claims']}
    default = set(graph['default_edge_ids'])
    expected = {
        'assertion-r004-v2-riemann-addresses-integrability',
        'assertion-r004-v2-riemann-defines-integral-state',
        'assertion-r004-v2-riemann-proves-integrability-criterion',
        'assertion-r004-v2-riemann-criterion-depends-integral-state',
    }
    assert expected <= default
    assert claims['assertion-r004-v2-riemann-defines-integral-state']['object_kind'] == 'ConceptState'
    assert claims['assertion-r004-v2-riemann-proves-integrability-criterion']['object_kind'] == 'Result'
