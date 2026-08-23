from scripts.common import ROOT, load_yaml_files
from scripts.semantic_network import build_semantic_network


def network():
    return build_semantic_network(
        load_yaml_files(ROOT / 'data/entities'),
        load_yaml_files(ROOT / 'data/questions'),
        load_yaml_files(ROOT / 'data/concept_states'),
        load_yaml_files(ROOT / 'data/assertions'),
    )


def default_ids():
    return set(network()['default_edge_ids'])


def test_r003_exposes_dirichlet_result_and_function_state():
    default = default_ids()
    expected = {
        'assertion-r003-v2-dirichlet-1829-proves-convergence',
        'assertion-r003-v2-dirichlet-1829-uses-discontinuous-state',
        'assertion-r003-v2-dirichlet-1837-uses-function-state',
    }
    assert expected <= default


def test_r005_exposes_quantified_control_as_historical_states():
    graph = network()
    claims = {c['id']: c for c in graph['claims']}
    default = set(graph['default_edge_ids'])
    expected = {
        'assertion-r005-v2-bolzano-uses-control-state',
        'assertion-r005-v2-cauchy-1823-uses-control-state',
        'assertion-r005-v2-weierstrass-1861-uses-control-state',
        'assertion-r005-v2-heine-1872-uses-control-state',
    }
    assert expected <= default
    assert all(claims[x]['object_kind'] == 'ConceptState' for x in expected)


def test_r006_exposes_solving_problem_results_and_substitution_state():
    default = default_ids()
    expected = {
        'assertion-r006-v2-lagrange-addresses-solvability',
        'assertion-r006-v2-abel-1824-proves-impossibility',
        'assertion-r006-v2-galois-addresses-solvability',
        'assertion-r006-v2-galois-uses-substitution-state',
        'assertion-r006-v2-galois-proves-solvability-criterion',
    }
    assert expected <= default


def test_r007_exposes_gauss_work_curvature_and_egregium():
    default = default_ids()
    expected = {
        'assertion-r007-v2-gauss-defines-curvature-state',
        'assertion-r007-v2-gauss-uses-applicability-state',
        'assertion-r007-v2-gauss-proves-egregium',
        'assertion-r007-v2-egregium-depends-curvature-state',
    }
    assert expected <= default


def test_r009_exposes_kummer_dedekind_factorization_and_revision_chain():
    default = default_ids()
    expected = {
        'assertion-r009-v2-kummer-addresses-factorization',
        'assertion-r009-v2-kummer-uses-ideal-divisor-state',
        'assertion-r009-v2-dedekind-1871-addresses-factorization',
        'assertion-r009-v2-dedekind-defines-ideal-state',
        'assertion-r009-v2-dedekind-proves-prime-factorization',
        'assertion-r009-v2-dedekind-1879-revises-1871',
        'assertion-r009-v2-dedekind-1894-revises-1879',
    }
    assert expected <= default
