from scripts.common import ROOT, load_yaml_files
from scripts.semantic_network import (
    PUBLISHABLE_STATUSES,
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


def test_broad_contributed_to_claims_are_retained_but_not_default_topology():
    entities, questions, states, assertions = canonical_rows()
    network = build_semantic_network(entities, questions, states, assertions)
    broad = [c for c in network['claims'] if c['relation_family'] == 'broad_association']
    assert broad
    default_ids = set(network['default_edge_ids'])
    assert all(c['id'] not in default_ids for c in broad)


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
    assert person['temporal_semantics'] == 'life_span'
    assert work['temporal_semantics'] == 'work_date'
    assert concept['temporal_semantics'] == 'diachronic_identity'


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
    assert relation_signature_error('authored', 'Person', 'Work') is None
    assert relation_signature_error('addresses', 'Work', 'Problem') is None
    assert relation_signature_error('defines', 'Work', 'ConceptState') is None
    assert relation_signature_error('uses', 'Work', 'Concept') is None
    assert relation_signature_error('uses', 'Work', 'ConceptState') is None
    assert relation_signature_error('proves', 'Work', 'Result') is None
    assert relation_signature_error('revises', 'Work', 'Work') is None

    assert relation_signature_error('defines', 'Person', 'ConceptState')
    assert relation_signature_error('addresses', 'Person', 'Problem')
    assert relation_signature_error('proves', 'Work', 'Concept')
    assert relation_signature_error('cites', 'Person', 'Work')


def test_semantic_audit_exposes_migration_queues():
    entities, questions, states, assertions = canonical_rows()
    audit = semantic_audit(entities, questions, states, assertions)
    queues = audit['review_queues']
    assert queues['broad_publishable_relations']
    assert queues['inquiry_layer_claims']
    assert 'unpublished_research_claims' in queues
