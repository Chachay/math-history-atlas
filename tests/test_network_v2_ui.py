from scripts.common import ROOT


def test_network_ui_consumes_semantic_v2_projection():
    source = (ROOT / 'app' / 'src' / 'main.tsx').read_text(encoding='utf-8')
    assert "semantic-network.json" in source
    assert "default_edge_ids" in source
    assert "Story = highlight, not lane" in source


def test_network_ui_does_not_build_topology_from_story_steps():
    source = (ROOT / 'app' / 'src' / 'main.tsx').read_text(encoding='utf-8')
    assert "buildNetworkLayout" not in source
    assert "story-overlay" not in source
    assert "node-question" not in source


def test_network_ui_states_questionframes_are_outside_default_topology():
    source = (ROOT / 'app' / 'src' / 'main.tsx').read_text(encoding='utf-8')
    assert "QuestionFrames stay in the Inquiry/Story layer" in source
