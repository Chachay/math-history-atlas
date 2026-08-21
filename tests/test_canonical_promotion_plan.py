from pathlib import Path

from scripts.plan_canonical_promotion import CanonicalEntity, classify_entity


def _canonical(id: str, type: str, name: str, path: str = "data/entities/test.yaml") -> CanonicalEntity:
    return CanonicalEntity(id=id, type=type, name=name, path=path, row={"id": id, "type": type, "name": name})


def test_exact_id_and_identity_fields_reuse_existing_entity():
    canonical = [_canonical("person-heine", "Person", "Eduard Heine")]
    result = classify_entity(
        {"id": "person-heine", "type": "Person", "canonical_name": "Eduard Heine"},
        canonical,
    )
    assert result["status"] == "REUSE"
    assert result["path"] == "data/entities/test.yaml"


def test_exact_id_with_different_identity_is_conflict():
    canonical = [_canonical("person-heine", "Person", "Eduard Heine")]
    result = classify_entity(
        {"id": "person-heine", "type": "Person", "canonical_name": "Different Person"},
        canonical,
    )
    assert result["status"] == "CONFLICT"
    assert "differs" in result["reason"]


def test_same_name_under_different_id_requires_explicit_identity_decision():
    canonical = [_canonical("person-heine", "Person", "Eduard Heine")]
    result = classify_entity(
        {"id": "person-eduard-heine", "type": "Person", "canonical_name": "Eduard Heine"},
        canonical,
    )
    assert result["status"] == "CONFLICT"
    assert result["candidates"] == [{"id": "person-heine", "path": "data/entities/test.yaml"}]


def test_new_entity_is_new_when_no_identity_candidate_exists():
    canonical = [_canonical("person-heine", "Person", "Eduard Heine")]
    result = classify_entity(
        {"id": "person-cantor", "type": "Person", "canonical_name": "Georg Cantor"},
        canonical,
    )
    assert result["status"] == "NEW"
