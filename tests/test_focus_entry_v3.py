from scripts.common import ROOT


def test_focus_explorer_is_mounted_without_replacing_overview():
    html=(ROOT/'app/index.html').read_text(encoding='utf-8')
    entry=(ROOT/'app/src/focusEntry.tsx').read_text(encoding='utf-8')
    assert '<div id="root"></div>' in html
    assert '<div id="focus-root"></div>' in html
    assert '/src/main.tsx' in html
    assert '/src/focusEntry.tsx' in html
    assert "path!=='network'" in entry
    assert 'NetworkFocusExplorer' in entry


def test_focus_entry_reads_v3_semantic_projections():
    source=(ROOT/'app/src/focusEntry.tsx').read_text(encoding='utf-8')
    assert "semantic-network.json" in source
    assert "concept-evolution.json" in source
    assert "concept-function" in source
