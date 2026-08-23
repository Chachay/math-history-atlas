from __future__ import annotations

from collections import defaultdict
from scripts.common import ROOT, load_yaml_files


def _year(state: dict):
    return state.get('period', {}).get('from')


def build_concept_evolution():
    entities = load_yaml_files(ROOT / 'data/entities')
    states = load_yaml_files(ROOT / 'data/concept_states')
    assertions = load_yaml_files(ROOT / 'data/assertions')

    concepts = {row['id']: row for row in entities if row.get('type') == 'Concept'}
    entity_ids = {row['id'] for row in entities}
    states_by_concept = defaultdict(list)
    for state in states:
        states_by_concept[state['concept_id']].append(state)

    incident = defaultdict(list)
    state_ids = {state['id'] for state in states}
    for claim in assertions:
        if claim.get('status') not in {'historically_reviewed', 'accepted', 'published'}:
            continue
        if claim.get('subject') in state_ids:
            incident[claim['subject']].append(claim['id'])
        if claim.get('object') in state_ids:
            incident[claim['object']].append(claim['id'])

    rows = []
    for concept_id, concept in concepts.items():
        concept_states = sorted(states_by_concept.get(concept_id, []), key=lambda s: (_year(s) is None, _year(s) or 0, s['id']))
        rows.append({
            'concept_id': concept_id,
            'name': concept.get('name', concept_id),
            'fields': concept.get('fields', []),
            'states': [
                {
                    'id': state['id'],
                    'year': _year(state),
                    'period': state.get('period', {}),
                    'label': state.get('label', ''),
                    'claim_ids': incident.get(state['id'], []),
                }
                for state in concept_states
            ],
            # Ordering is deliberately non-causal. A later state is not asserted to
            # develop from an earlier one unless a reviewed claim says so.
            'timeline_semantics': 'attested_states_grouped_by_diachronic_identity',
        })

    return {
        'projection_version': 3,
        'concepts': rows,
        'notes': [
            'State order is chronological grouping, not a historical-causation claim.',
            'ConceptState detail remains evidence-bearing canonical data; this projection only groups it for exploration.',
        ],
    }
