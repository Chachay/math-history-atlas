from pathlib import Path

import pytest

from scripts.research_validation import (
    load_yaml_mapping,
    validate_packet,
    validate_resolution_semantics,
    validate_review,
)


def sample_packet():
    return {
        "research_unit": {"id": "R999"},
        "assertions": [{"id": "a1", "sources": ["src-1"]}],
        "sources": [{"id": "src-1"}],
    }


def sample_review():
    return {
        "review": {"research_unit_id": "R999"},
        "findings": [
            {
                "id": "f-revise",
                "classification": "REVISE",
                "target": {"section": "assertions", "id": "a1"},
                "proposed_change": {
                    "action": "replace_fields",
                    "fields": {"statement": "revised"},
                },
                "evidence": [{"source_id": "src-1"}],
            },
            {
                "id": "f-manual",
                "classification": "WEAK_EVIDENCE",
                "target": {"section": "assertions", "id": "a1"},
                "proposed_change": {"action": "manual_review", "reason": "preserve gap"},
            },
        ],
        "sources": [],
    }


def sample_resolution():
    return {
        "research_unit_id": "R999",
        "decisions": [
            {
                "review_key": "finding:f-revise",
                "item_id": "f-revise",
                "critic_classification": "REVISE",
                "decision": "accept_critic",
            },
            {
                "review_key": "finding:f-manual",
                "item_id": "f-manual",
                "critic_classification": "WEAK_EVIDENCE",
                "decision": "accept_critic",
            },
        ],
    }


def test_packet_rejects_duplicate_ids_and_missing_sources():
    packet = sample_packet()
    packet["assertions"].append({"id": "a1", "sources": ["src-missing"]})
    errors = validate_packet(packet)
    assert any("duplicate IDs" in error for error in errors)
    assert any("src-missing" in error for error in errors)


def test_review_targets_and_packet_sources_resolve():
    assert validate_review(sample_review(), sample_packet()) == []


def test_resolution_requires_critic_finding_ids_not_packet_item_ids():
    resolution = sample_resolution()
    resolution["decisions"][0]["item_id"] = "a1"
    errors = validate_resolution_semantics(sample_packet(), sample_review(), resolution)
    assert any("does not name a critic finding" in error for error in errors)
    assert any("f-revise" in error and "without human decisions" in error for error in errors)


def test_resolution_accepts_explicit_manual_review_action():
    assert validate_resolution_semantics(sample_packet(), sample_review(), sample_resolution()) == []


def test_resolution_rejects_stale_target():
    review = sample_review()
    review["findings"][0]["target"]["id"] = "missing"
    errors = validate_resolution_semantics(sample_packet(), review, sample_resolution())
    assert any("target matched 0" in error for error in errors)


def test_invalid_colon_bearing_yaml_fails_parse(tmp_path: Path):
    path = tmp_path / "bad.yaml"
    path.write_text("research_unit:\n  id: R999\nsource:\n  title: Notiz: Beweis\n", encoding="utf-8")
    with pytest.raises(ValueError, match="not valid YAML"):
        load_yaml_mapping(path)
