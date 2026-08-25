from scripts.common import ROOT


def test_story_semantic_map_component_preserves_story_vs_network_boundary():
    source=(ROOT/'app/src/components/LocalSemanticMap.tsx').read_text(encoding='utf-8')
    assert 'storySeeds' in source
    assert 'assertion_refs' in source
    assert 'expandConceptWindows' in source
    assert 'Chronological order groups attested states' in source
    assert "mode==='story'" in source
    assert 'initialFocusId' in source


def test_story_route_mounts_local_semantic_map():
    source=(ROOT/'app/src/storyMapEntry.tsx').read_text(encoding='utf-8')
    assert "parts[0]==='story'" in source
    assert 'LocalSemanticMap' in source
    assert 'story-layout' in source
    assert 'legacyAssertions={payload.assertions}' in source


def test_network_route_reuses_same_local_semantic_map_without_story_overlay():
    source=(ROOT/'app/src/networkMapEntry.tsx').read_text(encoding='utf-8')
    assert "mode=\"network\"" in source
    assert 'LocalSemanticMap' in source
    assert 'initialFocusId={initial}' in source
    assert 'story=' not in source


def test_semantic_maps_are_loaded_by_app_shell():
    html=(ROOT/'app/index.html').read_text(encoding='utf-8')
    assert '/src/storyMapEntry.tsx' in html
    assert '/src/networkMapEntry.tsx' in html
