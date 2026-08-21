from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from scripts.promote_packet import ACCEPTED_DECISIONS, match_target


MATERIAL_CLASSES = {"REVISE", "WEAK_EVIDENCE", "REJECT"}


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"{path} is not valid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path} does not contain a YAML mapping.")
    return data


def _duplicate_ids(rows: Any, label: str) -> list[str]:
    if not isinstance(rows, list):
        return []
    ids = [str(row.get("id", "")).strip() for row in rows if isinstance(row, dict) and row.get("id")]
    return sorted({item for item in ids if ids.count(item) > 1})


def _source_ids(data: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for row in data.get("sources", []) or []:
        if isinstance(row, dict) and row.get("id"):
            result.add(str(row["id"]))
    return result


def _source_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "sources" and isinstance(child, list):
                refs.update(str(x) for x in child if isinstance(x, str))
            elif key == "source_id" and isinstance(child, str):
                refs.add(child)
            else:
                refs.update(_source_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(_source_refs(child))
    return refs


def validate_packet(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    unit = packet.get("research_unit")
    if not isinstance(unit, dict) or not unit.get("id"):
        errors.append("packet missing research_unit.id")

    for section in (
        "research_questions",
        "entities",
        "assertions",
        "question_transitions",
        "intersection_candidates",
        "concept_state_candidates",
        "story_candidates",
        "uncertainties",
    ):
        dupes = _duplicate_ids(packet.get(section), section)
        if dupes:
            errors.append(f"duplicate IDs in {section}: {dupes}")

    source_ids = _source_ids(packet)
    missing = sorted(ref for ref in _source_refs(packet) if ref.startswith(("src-", "source-")) and ref not in source_ids)
    if missing:
        errors.append(f"unresolved packet source refs: {missing}")
    return errors


def validate_review(
    review: dict[str, Any],
    packet: dict[str, Any],
    *,
    require_current_targets: bool = True,
) -> list[str]:
    errors: list[str] = []
    header = review.get("review")
    if not isinstance(header, dict) or not header.get("research_unit_id"):
        errors.append("review missing review.research_unit_id")

    findings = review.get("findings")
    if not isinstance(findings, list):
        return errors + ["review findings must be a list"]

    dupes = _duplicate_ids(findings, "findings")
    if dupes:
        errors.append(f"duplicate review finding IDs: {dupes}")

    known_sources = _source_ids(packet) | _source_ids(review)
    missing_sources = sorted(ref for ref in _source_refs(review) if ref.startswith(("src-", "source-")) and ref not in known_sources)
    if missing_sources:
        errors.append(f"unresolved review source refs: {missing_sources}")

    if require_current_targets:
        for row in findings:
            if not isinstance(row, dict):
                errors.append("review finding is not a mapping")
                continue
            finding_id = str(row.get("id", "<missing>"))
            target = row.get("target")
            if target:
                try:
                    _, _, matches = match_target(packet, target)
                except (ValueError, RuntimeError) as exc:
                    errors.append(f"{finding_id}: invalid target: {exc}")
                    continue
                if len(matches) != 1:
                    errors.append(f"{finding_id}: target matched {len(matches)} packet objects")
    return errors


def validate_resolution_semantics(
    packet: dict[str, Any],
    review: dict[str, Any],
    resolution: dict[str, Any],
    *,
    require_current_targets: bool = True,
) -> list[str]:
    errors: list[str] = []
    findings = {
        str(row.get("id")): row
        for row in review.get("findings", [])
        if isinstance(row, dict) and row.get("id")
    }
    decisions = resolution.get("decisions")
    if not isinstance(decisions, list):
        return ["resolution decisions must be a list"]

    decision_by_id: dict[str, dict[str, Any]] = {}
    for decision in decisions:
        if not isinstance(decision, dict):
            errors.append("resolution decision is not a mapping")
            continue
        item_id = str(decision.get("item_id", "")).strip()
        if not item_id:
            errors.append("resolution decision missing item_id")
            continue
        if item_id in decision_by_id:
            errors.append(f"duplicate resolution decision for {item_id}")
            continue
        decision_by_id[item_id] = decision
        finding = findings.get(item_id)
        if finding is None:
            errors.append(f"resolution item_id {item_id} does not name a critic finding")
            continue
        expected_key = f"finding:{item_id}"
        if decision.get("review_key") != expected_key:
            errors.append(f"{item_id}: review_key must be {expected_key}")
        if decision.get("critic_classification") != finding.get("classification"):
            errors.append(f"{item_id}: critic_classification does not match current review")

        if decision.get("decision") in ACCEPTED_DECISIONS:
            target = finding.get("target")
            proposed = finding.get("proposed_change")
            if not target:
                errors.append(f"{item_id}: accepted finding has no target")
            elif require_current_targets:
                try:
                    _, _, matches = match_target(packet, target)
                    if len(matches) != 1:
                        errors.append(f"{item_id}: target matched {len(matches)} packet objects")
                except (ValueError, RuntimeError) as exc:
                    errors.append(f"{item_id}: invalid target: {exc}")
            if not isinstance(proposed, dict) or not proposed.get("action"):
                errors.append(f"{item_id}: accepted finding has no promotion action")

    material_ids = {
        finding_id
        for finding_id, row in findings.items()
        if str(row.get("classification", "")).upper() in MATERIAL_CLASSES
    }
    unresolved = sorted(material_ids - set(decision_by_id))
    if unresolved:
        errors.append(f"material findings without human decisions: {unresolved}")

    return errors


def require_no_errors(errors: list[str], *, label: str) -> None:
    if errors:
        detail = "\n".join(f"- {item}" for item in errors)
        raise RuntimeError(f"{label} validation failed:\n{detail}")
