from __future__ import annotations

from collections import defaultdict

from scripts.common import ROOT, load_yaml_files
from scripts.semantic_network import normalize_assertions


def _year(state: dict) -> int | None:
    return state.get('period', {}).get('from')


def build_atlas_projection(entities: list[dict], questions: list[dict], concept_states: list[dict], assertions: list[dict]) -> dict:
    """Aggregate canonical semantic data at Field -> Concept -> ConceptState scale.

    Reader projection only: chronology groups attested states but does not create
    historical causation or development claims.
    """
    fields = load_yaml_files(ROOT / 'data/fields')
    concepts = {e['id']: e for e in entities if e.get('type') == 'Concept'}
    nodes = {e['id']: e for e in entities}
    claims = normalize_assertions(entities, questions, concept_states, assertions)
    typed = [c for c in claims if c.get('publishable') and c.get('default_network_visible') and c.get('semantic_layer') in {'historical', 'mathematical'}]

    incident: dict[str, set[str]] = defaultdict(set)
    for claim in typed:
        incident[claim['subject']].add(claim['object'])
        incident[claim['object']].add(claim['subject'])

    states_by_concept: dict[str, list[dict]] = defaultdict(list)
    for state in concept_states:
        states_by_concept[state['concept_id']].append(state)

    concept_rows = []
    for concept_id, concept in concepts.items():
        state_rows = []
        related_ids: set[str] = set()
        for state in sorted(states_by_concept.get(concept_id, []), key=lambda s: (_year(s) is None, _year(s) or 0, s['id'])):
            neighbors = sorted(incident.get(state['id'], set()))
            related_ids.update(neighbors)
            state_rows.append({'id': state['id'], 'year': _year(state), 'period': state.get('period', {}), 'label': state.get('label', ''), 'related_node_ids': neighbors})
        related_by_kind: dict[str, list[str]] = defaultdict(list)
        for node_id in sorted(related_ids):
            node = nodes.get(node_id)
            if node:
                related_by_kind[node.get('type', 'Other')].append(node_id)
        years = [row['year'] for row in state_rows if row['year'] is not None]
        concept_rows.append({'id': concept_id, 'name': concept.get('name', concept_id), 'fields': concept.get('fields', []), 'state_count': len(state_rows), 'first_attested_state_year': min(years) if years else None, 'last_attested_state_year': max(years) if years else None, 'states': state_rows, 'related': dict(related_by_kind)})

    field_rows = []
    for field in fields:
        members = [row for row in concept_rows if field['id'] in row.get('fields', [])]
        members.sort(key=lambda row: (row['first_attested_state_year'] is None, row['first_attested_state_year'] or 0, row['name']))
        state_ids = [state['id'] for row in members for state in row['states']]
        related_ids = sorted({node_id for row in members for values in row['related'].values() for node_id in values})
        field_rows.append({**field, 'concept_ids': [row['id'] for row in members], 'concept_count': len(members), 'concept_state_ids': state_ids, 'concept_state_count': len(state_ids), 'related_node_ids': related_ids})

    return {
        'projection_version': 3,
        'fields': field_rows,
        'concepts': concept_rows,
        'cross_field_concepts': [{'concept_id': row['id'], 'fields': row['fields']} for row in concept_rows if len(row.get('fields', [])) > 1],
        'notes': [
            'Atlas aggregation groups semantic data; it does not create new historical claims.',
            'ConceptState chronology is descriptive unless an evidence-bearing development relation exists elsewhere.',
            'Concept identities bridge field-scale Atlas views and historically situated Network states.',
        ],
    }
