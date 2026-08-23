from scripts.common import ROOT


def test_atlas_v3_is_mounted_alongside_legacy_atlas():
    html=(ROOT/'app/index.html').read_text(encoding='utf-8')
    source=(ROOT/'app/src/atlasEntry.tsx').read_text(encoding='utf-8')
    assert '<div id="atlas-v3-root"></div>' in html
    assert '/src/atlasEntry.tsx' in html
    assert "atlas-projection.json" in source
    assert 'Atlas as a concept landscape' in source


def test_atlas_concepts_link_into_network_focus():
    source=(ROOT/'app/src/atlasEntry.tsx').read_text(encoding='utf-8')
    assert '#/network?field=' in source
    assert '&focus=' in source
    assert 'Concepts crossing field boundaries' in source
    assert 'slice(0,7)' in source
