from scripts.common import ROOT


def test_network_ui_consumes_semantic_v2_projection():
    source = (ROOT / 'app' / 'src' / 'main.tsx').read_text(encoding='utf-8')
    assert "semantic-network.json" in source
    assert "default_edge_ids" in source
    assert "Story selection highlights the historical path" in source


def test_network_ui_does_not_build_topology_from_story_steps():
    source = (ROOT / 'app' / 'src' / 'main.tsx').read_text(encoding='utf-8')
    assert "buildNetworkLayout" not in source
    assert "story-overlay" not in source
    assert "node-question" not in source


def test_network_ui_keeps_questionframes_outside_default_topology():
    source = (ROOT / 'app' / 'src' / 'main.tsx').read_text(encoding='utf-8')
    assert "without importing Story questions into the graph" in source


def test_network_ui_supports_focus_context_and_folded_concepts():
    source = (ROOT / 'app' / 'src' / 'main.tsx').read_text(encoding='utf-8')
    assert "focusId" in source
    assert "focusRefs" in source
    assert "Show concept identities" in source
    assert "showConcepts" in source
    assert ">Details</button>" in source


def test_network_tap_focus_does_not_open_detail_sheet():
    source = (ROOT / 'app' / 'src' / 'main.tsx').read_text(encoding='utf-8')
    assert "onClick={()=>setFocusId(p.node.id)}" in source
    assert "SemanticNodeSheet node={focusedNode}" in source


def test_network_story_overlay_projects_to_semantic_endpoints():
    source = (ROOT / 'app' / 'src' / 'main.tsx').read_text(encoding='utf-8')
    assert "storyNodeIds" in source
    assert "selectedAssertionIds.has(c.id)" in source
    assert "storyNodeIds?.has(edge.subject) || storyNodeIds?.has(edge.object)" in source


def test_network_edges_use_shape_ports_and_straight_vertical_routes():
    source = (ROOT / 'app' / 'src' / 'main.tsx').read_text(encoding='utf-8')
    assert "function nodeHalfSize" in source
    assert "function routeSemanticEdge" in source
    assert "Math.abs(dx) < 4" in source
    assert " L${tx} ${ty}" in source


def test_network_labels_wrap_without_semantic_truncation():
    source = (ROOT / 'app' / 'src' / 'main.tsx').read_text(encoding='utf-8')
    css = (ROOT / 'app' / 'src' / 'style.css').read_text(encoding='utf-8')
    assert "wrapLabel(node.name" in source
    assert "short(node.name" not in source
    assert ".network-scroll" in css
    assert "min-width:980px" in css


def test_reader_surfaces_do_not_fallback_to_internal_ids():
    source = (ROOT / 'app' / 'src' / 'main.tsx').read_text(encoding='utf-8')
    assert "label=item?" not in source
    assert "other?.name ||" not in source
    assert "a.subject===person.id?a.object:a.subject" not in source
