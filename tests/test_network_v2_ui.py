from scripts.common import ROOT


def test_network_ui_consumes_semantic_v2_projection():
    source = (ROOT / 'app' / 'src' / 'main.tsx').read_text(encoding='utf-8')
    assert "semantic-network.json" in source
    assert "default_edge_ids" in source
    assert "QuestionFrames remain in the Inquiry/Story layer" in source


def test_network_ui_does_not_build_topology_from_story_steps():
    source = (ROOT / 'app' / 'src' / 'main.tsx').read_text(encoding='utf-8')
    assert "buildNetworkLayout" not in source
    assert "story-overlay" not in source
    assert "node-question" not in source


def test_network_ui_states_questionframes_are_outside_default_topology():
    source = (ROOT / 'app' / 'src' / 'main.tsx').read_text(encoding='utf-8')
    assert "QuestionFrames remain in the Inquiry/Story layer" in source


def test_network_ui_supports_focus_context_and_folded_concepts():
    source = (ROOT / 'app' / 'src' / 'main.tsx').read_text(encoding='utf-8')
    assert "focusId" in source
    assert "focusRefs" in source
    assert "Show concept identities" in source
    assert "showConcepts" in source


def test_network_labels_wrap_without_semantic_truncation():
    source = (ROOT / 'app' / 'src' / 'main.tsx').read_text(encoding='utf-8')
    css = (ROOT / 'app' / 'src' / 'style.css').read_text(encoding='utf-8')
    assert "wrapLabel(node.name" in source
    assert "short(node.name" not in source
    assert ".network-scroll" in css
    assert "min-width:980px" in css
