from scripts.plan_canonical_promotion import CanonicalEntity, build_plan, classify_entity


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


def test_r008_replay_reuses_heine_and_riemann_and_preserves_manual_exclusion():
    plan = build_plan("R008")
    by_id = {row["id"]: row for row in plan["entities"]}
    assert by_id["person-heine"]["status"] == "REUSE"
    assert by_id["person-riemann"]["status"] == "REUSE"

    excluded = plan["assertions"]["excluded_or_manual"]
    assert any(row.get("id") == "r008-a009" and row.get("action") == "manual_review" for row in excluded)
