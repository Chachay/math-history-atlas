from scripts.common import ROOT, load_yaml_files
from scripts.semantic_network import (
    PUBLISHABLE_STATUSES,
    PRECISE_NETWORK_PREDICATES,
    build_inquiry_graph,
    build_semantic_network,
    normalize_assertions,
    semantic_audit,
)
from scripts.validate import relation_signature_error


def canonical_rows():
    return (
        load_yaml_files(ROOT / 'data/entities'),
        load_yaml_files(ROOT / 'data/questions'),
        load_yaml_files(ROOT / 'data/concept_states'),
        load_yaml_files(ROOT / 'data/assertions'),
    )


def test_question_frames_are_not_semantic_network_nodes():
    entities, questions, states, assertions = canonical_rows()
    graph = build_semantic_network(entities, questions, states, assertions)
    node_ids = {n['id'] for n in graph['nodes']}
    assert not ({q['id'] for q in questions} & node_ids)
    assert all(n['node_kind'] != 'QuestionFrame' for n in graph['nodes'])


def test_inquiry_layer_contains_question_grounding_claims_only():
    entities, questions, states, assertions = canonical_rows()
    graph = build_inquiry_graph(entities, questions, states, assertions)
    question_ids = {q['id'] for q in questions}
    assert graph['claims']
    assert all(c['subject'] in question_ids or c['object'] in question_ids for c in graph['claims'])
    assert all(c['semantic_layer'] == 'inquiry' for c in graph['claims'])
    assert all(q['temporal_semantics'] == 'editorial_anchor' for q in graph['question_frames'])


def test_unreviewed_claims_never_enter_reader_projections():
    entities, questions, states, assertions = canonical_rows()
    network = build_semantic_network(entities, questions, states, assertions)
    inquiry = build_inquiry_graph(entities, questions, states, assertions)
    reader_ids = {c['id'] for c in network['claims']} | {c['id'] for c in inquiry['claims']}
    unreviewed = {a['id'] for a in assertions if a['status'] not in PUBLISHABLE_STATUSES}
    assert not (reader_ids & unreviewed)


def test_broad_and_legacy_claims_are_retained_but_not_default_topology():
    entities, questions, states, assertions = canonical_rows()
    network = build_semantic_network(entities, questions, states, assertions)
    default_ids = set(network['default_edge_ids'])
    broad = [c for c in network['claims'] if c['relation_precision'] == 'broad']
    legacy = [c for c in network['claims'] if c['relation_precision'] == 'legacy']
    assert broad
    assert legacy
    assert all(c['id'] not in default_ids for c in broad)
    assert all(c['id'] not in default_ids for c in legacy)
    assert all(c['predicate'] in PRECISE_NETWORK_PREDICATES for c in network['claims'] if c['id'] in default_ids)


def test_concept_states_are_explicit_nodes_with_structural_identity_edges():
    entities, questions, states, assertions = canonical_rows()
    network = build_semantic_network(entities, questions, states, assertions)
    state_ids = {s['id'] for s in states}
    node_ids = {n['id'] for n in network['nodes']}
    assert state_ids <= node_ids
    state_edges = {e['subject']: e['object'] for e in network['structural_edges']}
    assert all(state_edges[s['id']] == s['concept_id'] for s in states)
    state_nodes = [n for n in network['nodes'] if n['node_kind'] == 'ConceptState']
    assert state_nodes and all(n['temporal_semantics'] == 'attested_state' for n in state_nodes)


def test_temporal_semantics_are_node_type_specific():
    entities, questions, states, assertions = canonical_rows()
    network = build_semantic_network(entities, questions, states, assertions)
    person = next(n for n in network['nodes'] if n['node_kind'] == 'Person')
    work = next(n for n in network['nodes'] if n['node_kind'] == 'Work')
    concept = next(n for n in network['nodes'] if n['node_kind'] == 'Concept')
    problem = next(n for n in network['nodes'] if n['node_kind'] == 'Problem')
    result = next(n for n in network['nodes'] if n['node_kind'] == 'Result')
    assert person['temporal_semantics'] == 'life_span'
    assert work['temporal_semantics'] == 'work_date'
    assert concept['temporal_semantics'] == 'diachronic_identity'
    assert problem['temporal_semantics'] == 'problem_period'
    assert result['temporal_semantics'] == 'result_date'


def test_perspective_and_semantic_layer_are_orthogonal():
    entities, questions, states, assertions = canonical_rows()
    claims = normalize_assertions(entities, questions, states, assertions)
    historiographic_historical = [
        c for c in claims
        if c['claim_mode'] == 'historiographic' and c['semantic_layer'] == 'historical'
    ]
    assert historiographic_historical
    assert all(c['perspective'] == 'later_interpretation' for c in historiographic_historical)


def test_precise_relation_signatures_are_typed():
    valid = [
        ('authored', 'Person', 'Work'),
        ('addresses', 'Work', 'Problem'),
        ('concerns', 'Problem', 'ConceptState'),
        ('defines', 'Work', 'ConceptState'),
        ('introduces', 'Work', 'ConceptState'),
        ('uses', 'Work', 'Concept'),
        ('uses', 'Work', 'ConceptState'),
        ('proves', 'Work', 'Result'),
        ('resolves', 'Result', 'Problem'),
        ('strengthens', 'Result', 'Result'),
        ('depends_on', 'Result', 'ConceptState'),
        ('generalizes', 'Concept', 'Concept'),
        ('develops', 'Work', 'Work'),
        ('revises', 'Work', 'Work'),
        ('cites', 'Work', 'Work'),
    ]
    for predicate, subject_kind, object_kind in valid:
        assert relation_signature_error(predicate, subject_kind, object_kind) is None

    assert relation_signature_error('defines', 'Person', 'ConceptState')
    assert relation_signature_error('addresses', 'Person', 'Problem')
    assert relation_signature_error('proves', 'Work', 'Concept')
    assert relation_signature_error('cites', 'Person', 'Work')
    assert relation_signature_error('strengthens', 'Work', 'Result')


def test_r008_fixture_exposes_work_result_and_concept_state_structure():
    entities, questions, states, assertions = canonical_rows()
    network = build_semantic_network(entities, questions, states, assertions)
    claims = {c['id']: c for c in network['claims']}
    default_ids = set(network['default_edge_ids'])

    expected = {
        'assertion-r008-v2-heine-addresses-uniqueness',
        'assertion-r008-v2-cantor-1870-proves',
        'assertion-r008-v2-cantor-1871-strengthens-1870',
        'assertion-r008-v2-cantor-1872-defines-derived',
        'assertion-r008-v2-cantor-1872-proves',
        'assertion-r008-v2-cantor-1872-depends-derived',
    }
    assert expected <= default_ids
    assert claims['assertion-r008-v2-cantor-1872-defines-derived']['object_kind'] == 'ConceptState'
    assert claims['assertion-r008-v2-cantor-1872-proves']['object_kind'] == 'Result'
    assert 'assertion-r008-convergence-to-uniqueness-question' not in default_ids


def test_r010_fixture_preserves_direct_borel_handoff_without_inventing_jordan_causation():
    entities, questions, states, assertions = canonical_rows()
    network = build_semantic_network(entities, questions, states, assertions)
    claims = {c['id']: c for c in network['claims']}
    default_ids = set(network['default_edge_ids'])

    assert 'assertion-r010-v2-lebesgue-cites-borel' in default_ids
    assert claims['assertion-r010-v2-lebesgue-cites-borel']['predicate'] == 'cites'
    assert 'assertion-r010-v2-lebesgue-addresses-riemann-gap' in default_ids
    assert 'assertion-r010-v2-lebesgue-defines-integral-state' in default_ids
    assert 'assertion-r010-v2-modern-lebesgue-generalizes-riemann' in default_ids
    assert 'assertion-r010-lines-converge' not in default_ids

    # Jordan is represented by its own authored work/content state; the reviewed
    # Story convergence remains Inquiry, not a fabricated direct Jordan->Lebesgue edge.
    jordan = [c for c in claims.values() if c['subject'] == 'work-jordan-integrals-1892' and c['default_network_visible']]
    assert jordan
    assert not any(c['object'] == 'work-lebesgue-generalization-1901' for c in jordan)


def test_semantic_audit_exposes_migration_queues():
    entities, questions, states, assertions = canonical_rows()
    audit = semantic_audit(entities, questions, states, assertions)
    queues = audit['review_queues']
    assert queues['broad_publishable_relations']
    assert queues['legacy_publishable_relations']
    assert queues['inquiry_layer_claims']
    assert 'unpublished_research_claims' in queues
