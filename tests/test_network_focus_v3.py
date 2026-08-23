from scripts.common import ROOT


def test_focus_explorer_is_one_node_navigation_not_force_graph():
    source = (ROOT / 'app' / 'src' / 'components' / 'NetworkFocusExplorer.tsx').read_text(encoding='utf-8')
    assert 'NetworkFocusExplorer' in source
    assert 'focusId' in source
    assert 'trail' in source
    assert 'focus-breadcrumbs' in source
    assert 'force' not in source.lower()


def test_focus_explorer_groups_adjacent_semantic_relations():
    source = (ROOT / 'app' / 'src' / 'components' / 'NetworkFocusExplorer.tsx').read_text(encoding='utf-8')
    assert 'groupAdjacentEdges' in source
    assert 'Explore from here' in source
    assert 'totalChoices > 7' in source
    assert '<details' in source


def test_focus_explorer_exposes_concept_evolution_without_causal_claim():
    source = (ROOT / 'app' / 'src' / 'components' / 'NetworkFocusExplorer.tsx').read_text(encoding='utf-8')
    assert 'getConceptEvolution' in source
    assert 'Concept evolution' in source
    assert 'chronology alone does not assert causation' in source


def test_focus_explorer_searches_and_records_actual_navigation_history():
    source = (ROOT / 'app' / 'src' / 'components' / 'NetworkFocusExplorer.tsx').read_text(encoding='utf-8')
    assert 'searchNodes' in source
    assert 'setTrail(current => [...current, id])' in source
    assert 'current.slice(0, index + 1)' in source
