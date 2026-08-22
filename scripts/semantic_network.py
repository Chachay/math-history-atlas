from __future__ import annotations

from collections import Counter
from typing import Iterable

PUBLISHABLE_STATUSES = {'historically_reviewed', 'accepted', 'published'}

PERSPECTIVE_TO_MODE = {
    'historical': 'historical',
    'later_interpretation': 'historiographic',
    'modern_abstraction': 'mathematical_retrospective',
}

PREDICATE_FAMILY = {
    'authored': 'documentary',
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

# V2 does not pretend that every legacy predicate has the same semantic precision.
# Broad predicates stay queryable but are not part of the default reader topology.
BROAD_FAMILIES = {'broad_association'}


def node_kind_map(entities: list[dict], questions: list[dict], concept_states: list[dict]) -> dict[str, str]:
    kinds = {row['id']: row['type'] for row in entities}
    kinds.update({row['id']: 'QuestionFrame' for row in questions})
    kinds.update({row['id']: 'ConceptState' for row in concept_states})
    return kinds


def semantic_layer(assertion: dict, kinds: dict[str, str]) -> str:
    explicit = assertion.get('semantic_layer')
    if explicit:
        return explicit
    subject_kind = kinds.get(assertion['subject'])
    object_kind = kinds.get(assertion['object'])
    if 'QuestionFrame' in {subject_kind, object_kind}:
        return 'inquiry'
    if assertion.get('perspective') == 'modern_abstraction':
        return 'mathematical'
    return 'historical'


def relation_family(assertion: dict, layer: str) -> str:
    explicit = assertion.get('relation_family')
    if explicit:
        return explicit
    if layer == 'inquiry':
        return 'inquiry'
    return PREDICATE_FAMILY.get(assertion.get('predicate', ''), 'unclassified')


def normalize_assertion(assertion: dict, kinds: dict[str, str]) -> dict:
    layer = semantic_layer(assertion, kinds)
    family = relation_family(assertion, layer)
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
        'relation_precision': 'broad' if family in BROAD_FAMILIES else 'typed',
        'publishable': publishable,
        'default_network_visible': (
            publishable
            and layer in {'historical', 'mathematical'}
            and family not in BROAD_FAMILIES
            and family != 'unclassified'
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
    nodes = [{**row, 'node_kind': row['type']} for row in entities]
    for state in concept_states:
        nodes.append({
            'id': state['id'],
            'node_kind': 'ConceptState',
            'type': 'ConceptState',
            'name': state['label'],
            'concept_id': state['concept_id'],
            'period': state['period'],
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
        'question_frames': [
            {
                **q,
                'node_kind': 'QuestionFrame',
                'editorial': True,
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
        'claim_modes': dict(Counter(c['claim_mode'] for c in claims)),
    }

    broad = [c['id'] for c in claims if c['relation_precision'] == 'broad' and c['publishable']]
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
        'counts': counts,
        'review_queues': {
            'broad_publishable_relations': broad,
            'inquiry_layer_claims': inquiry,
            'unpublished_research_claims': unpublished,
            'unclassified_relations': unclassified,
            'historical_claims_targeting_concepts_with_states': historical_concept_targets,
        },
        'notes': [
            'Broad publishable relations remain queryable but are excluded from default Network topology.',
            'QuestionFrame claims belong to the editorial inquiry layer and are excluded from semantic-network.json.',
            'Candidate and source_checked claims never enter reader-facing semantic-network.json or inquiry-graph.json.',
            'Historical claims targeting a Concept that already has ConceptState records require later human migration review; they are not auto-rewritten.',
        ],
    }
