from __future__ import annotations

from collections import Counter

PUBLISHABLE_STATUSES = {'historically_reviewed', 'accepted', 'published'}

PERSPECTIVE_TO_MODE = {
    'historical': 'historical',
    'later_interpretation': 'historiographic',
    'modern_abstraction': 'mathematical_retrospective',
}

# Only predicates with an explicit semantic contract and validator-enforced
# domain/range are allowed to define the default Network topology.
PRECISE_NETWORK_PREDICATES = {
    'authored',
    'addresses',
    'concerns',
    'defines',
    'introduces',
    'uses',
    'proves',
    'resolves',
    'strengthens',
    'depends_on',
    'generalizes',
    'develops',
    'revises',
    'responds_to',
    'cites',
}

PREDICATE_FAMILY = {
    # Precise V2 vocabulary.
    'authored': 'documentary',
    'addresses': 'problem_relation',
    'concerns': 'problem_relation',
    'defines': 'conceptual_content',
    'introduces': 'conceptual_content',
    'uses': 'conceptual_content',
    'proves': 'result_relation',
    'resolves': 'result_relation',
    'strengthens': 'result_relation',
    'depends_on': 'result_relation',
    'generalizes': 'development',
    'develops': 'development',
    'revises': 'documentary',
    'responds_to': 'documentary',
    'cites': 'documentary',
    # Legacy vocabulary retained during migration. These claims remain
    # queryable/evidence-bearing but do not define default topology until
    # migrated to a precise predicate.
    'raised_question': 'problem_relation',
    'spawned': 'problem_relation',
    'motivated': 'problem_relation',
    'reframed': 'development',
    'generalized': 'development',
    'split_into': 'development',
    'merged_with': 'development',
    'influenced': 'transmission',
    'contributed_to': 'broad_association',
}

TEMPORAL_SEMANTICS = {
    'Person': 'life_span',
    'Work': 'work_date',
    'Event': 'event_interval',
    'Problem': 'problem_period',
    'Result': 'result_date',
    'Concept': 'diachronic_identity',
    'ConceptState': 'attested_state',
    'QuestionFrame': 'editorial_anchor',
}

BROAD_FAMILIES = {'broad_association'}


def node_kind_map(entities: list[dict], questions: list[dict], concept_states: list[dict]) -> dict[str, str]:
    kinds = {row['id']: row['type'] for row in entities}
    kinds.update({row['id']: 'QuestionFrame' for row in questions})
    kinds.update({row['id']: 'ConceptState' for row in concept_states})
    return kinds


def semantic_layer(assertion: dict, kinds: dict[str, str]) -> str:
    subject_kind = kinds.get(assertion['subject'])
    object_kind = kinds.get(assertion['object'])
    # Ontology boundaries, not presentation hints.
    if 'QuestionFrame' in {subject_kind, object_kind}:
        return 'inquiry'
    if assertion.get('perspective') == 'modern_abstraction':
        return 'mathematical'
    explicit = assertion.get('semantic_layer')
    if explicit:
        return explicit
    return 'historical'


def relation_family(assertion: dict, layer: str) -> str:
    if layer == 'inquiry':
        return 'inquiry'
    explicit = assertion.get('relation_family')
    if explicit:
        return explicit
    return PREDICATE_FAMILY.get(assertion.get('predicate', ''), 'unclassified')


def relation_precision(assertion: dict, layer: str, family: str) -> str:
    if layer == 'inquiry':
        return 'inquiry'
    if family in BROAD_FAMILIES:
        return 'broad'
    if assertion.get('predicate') in PRECISE_NETWORK_PREDICATES:
        return 'typed'
    return 'legacy'


def normalize_assertion(assertion: dict, kinds: dict[str, str]) -> dict:
    layer = semantic_layer(assertion, kinds)
    family = relation_family(assertion, layer)
    precision = relation_precision(assertion, layer, family)
    status = assertion.get('status')
    publishable = status in PUBLISHABLE_STATUSES
    subject_kind = kinds.get(assertion['subject'], 'Unknown')
    object_kind = kinds.get(assertion['object'], 'Unknown')
    return {
        **assertion,
        'subject_kind': subject_kind,
        'object_kind': object_kind,
        'semantic_layer': layer,
        'claim_mode': PERSPECTIVE_TO_MODE.get(assertion.get('perspective'), 'unknown'),
        'relation_family': family,
        'relation_precision': precision,
        'publishable': publishable,
        'default_network_visible': (
            publishable
            and layer in {'historical', 'mathematical'}
            and precision == 'typed'
        ),
    }


def normalize_assertions(
    entities: list[dict],
    questions: list[dict],
    concept_states: list[dict],
    assertions: list[dict],
) -> list[dict]:
    kinds = node_kind_map(entities, questions, concept_states)
    return [normalize_assertion(row, kinds) for row in assertions]


def semantic_nodes(entities: list[dict], concept_states: list[dict]) -> list[dict]:
    nodes = [
        {
            **row,
            'node_kind': row['type'],
            'temporal_semantics': TEMPORAL_SEMANTICS.get(row['type'], 'unspecified'),
        }
        for row in entities
    ]
    for state in concept_states:
        nodes.append({
            'id': state['id'],
            'node_kind': 'ConceptState',
            'type': 'ConceptState',
            'name': state['label'],
            'concept_id': state['concept_id'],
            'period': state['period'],
            'temporal_semantics': TEMPORAL_SEMANTICS['ConceptState'],
        })
    return nodes


def structural_state_edges(concept_states: list[dict]) -> list[dict]:
    return [
        {
            'id': f"structural-{state['id']}-state-of",
            'subject': state['id'],
            'predicate': 'state_of',
            'object': state['concept_id'],
            'semantic_layer': 'historical',
            'relation_family': 'identity',
            'claim_mode': 'structural',
            'relation_precision': 'typed',
        }
        for state in concept_states
    ]


def build_semantic_network(
    entities: list[dict],
    questions: list[dict],
    concept_states: list[dict],
    assertions: list[dict],
) -> dict:
    claims = normalize_assertions(entities, questions, concept_states, assertions)
    published = [c for c in claims if c['publishable'] and c['semantic_layer'] != 'inquiry']
    return {
        'projection_version': 2,
        'nodes': semantic_nodes(entities, concept_states),
        'claims': published,
        'structural_edges': structural_state_edges(concept_states),
        'default_edge_ids': [c['id'] for c in published if c['default_network_visible']],
    }


def build_inquiry_graph(
    entities: list[dict],
    questions: list[dict],
    concept_states: list[dict],
    assertions: list[dict],
) -> dict:
    claims = normalize_assertions(entities, questions, concept_states, assertions)
    return {
        'projection_version': 2,
        'question_frames': [
            {
                **q,
                'node_kind': 'QuestionFrame',
                'editorial': True,
                'temporal_semantics': TEMPORAL_SEMANTICS['QuestionFrame'],
            }
            for q in questions
        ],
        'claims': [c for c in claims if c['publishable'] and c['semantic_layer'] == 'inquiry'],
    }


def build_research_claims(
    entities: list[dict],
    questions: list[dict],
    concept_states: list[dict],
    assertions: list[dict],
) -> dict:
    return {
        'projection_version': 2,
        'claims': normalize_assertions(entities, questions, concept_states, assertions),
    }


def semantic_audit(
    entities: list[dict],
    questions: list[dict],
    concept_states: list[dict],
    assertions: list[dict],
) -> dict:
    claims = normalize_assertions(entities, questions, concept_states, assertions)
    counts = {
        'claims': len(claims),
        'publishable_claims': sum(c['publishable'] for c in claims),
        'default_network_edges': sum(c['default_network_visible'] for c in claims),
        'layers': dict(Counter(c['semantic_layer'] for c in claims)),
        'relation_families': dict(Counter(c['relation_family'] for c in claims)),
        'relation_precision': dict(Counter(c['relation_precision'] for c in claims)),
        'claim_modes': dict(Counter(c['claim_mode'] for c in claims)),
    }

    broad = [c['id'] for c in claims if c['relation_precision'] == 'broad' and c['publishable']]
    legacy = [c['id'] for c in claims if c['relation_precision'] == 'legacy' and c['publishable']]
    inquiry = [c['id'] for c in claims if c['semantic_layer'] == 'inquiry']
    unpublished = [c['id'] for c in claims if not c['publishable']]
    unclassified = [c['id'] for c in claims if c['relation_family'] == 'unclassified']

    concepts_with_states = {state['concept_id'] for state in concept_states}
    historical_concept_targets = [
        c['id'] for c in claims
        if c['semantic_layer'] == 'historical'
        and c['object_kind'] == 'Concept'
        and c['object'] in concepts_with_states
        and c['subject_kind'] in {'Work', 'Person', 'Result', 'Problem'}
    ]

    return {
        'projection_version': 2,
        'counts': counts,
        'review_queues': {
            'broad_publishable_relations': broad,
            'legacy_publishable_relations': legacy,
            'inquiry_layer_claims': inquiry,
            'unpublished_research_claims': unpublished,
            'unclassified_relations': unclassified,
            'historical_claims_targeting_concepts_with_states': historical_concept_targets,
        },
        'notes': [
            'Only validator-contracted precise predicates define default Network topology.',
            'Broad and legacy publishable relations remain queryable but are excluded from default topology.',
            'QuestionFrame claims belong to the editorial inquiry layer and are excluded from semantic-network.json.',
            'Candidate and source_checked claims never enter reader-facing semantic-network.json or inquiry-graph.json.',
            'Historical claims targeting a Concept that already has ConceptState records require human migration review; they are not auto-rewritten.',
        ],
    }
