from scripts.common import ROOT


def test_atlas_semantic_entry_reads_generated_projection_and_links_to_concept_focus():
    source=(ROOT/'app/src/atlasSemanticEntry.tsx').read_text(encoding='utf-8')
    assert 'atlas-projection.json' in source
    assert '#/network?focus=' in source
    assert 'concept_state_count' in source
    assert 'SEMANTIC ATLAS' in source


def test_atlas_semantic_entry_is_loaded_by_app_shell():
    html=(ROOT/'app/index.html').read_text(encoding='utf-8')
    assert '/src/atlasSemanticEntry.tsx' in html
