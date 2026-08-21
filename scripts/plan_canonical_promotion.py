from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class CanonicalEntity:
    id: str
    type: str
    name: str
    path: str
    row: dict[str, Any]


def _load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _one(directory: Path, pattern: str) -> Path:
    matches = sorted(directory.glob(pattern))
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one {pattern} in {directory}, found {len(matches)}")
    return matches[0]


def _entity_name(row: dict[str, Any]) -> str:
    return str(row.get("canonical_name") or row.get("name") or "").strip()


def _norm(value: str) -> str:
    return " ".join(value.casefold().split())


def load_canonical_entities(root: Path = ROOT) -> list[CanonicalEntity]:
    result: list[CanonicalEntity] = []
    for path in sorted((root / "data/entities").glob("*.yaml")):
        rows = _load_yaml(path) or []
        if isinstance(rows, dict):
            rows = [rows]
        for row in rows:
            if not isinstance(row, dict) or not row.get("id"):
                continue
            result.append(
                CanonicalEntity(
                    id=str(row["id"]),
                    type=str(row.get("type", "")),
                    name=_entity_name(row),
                    path=str(path.relative_to(root)),
                    row=row,
                )
            )
    return result


def classify_entity(
    candidate: dict[str, Any],
    canonical: list[CanonicalEntity],
) -> dict[str, Any]:
    candidate_id = str(candidate.get("id", "")).strip()
    candidate_type = str(candidate.get("type", "")).strip()
    candidate_name = _entity_name(candidate)
    if not candidate_id or not candidate_type or not candidate_name:
        return {
            "status": "CONFLICT",
            "id": candidate_id or "<missing>",
            "reason": "candidate entity requires id, type, and canonical/display name",
        }

    exact = [row for row in canonical if row.id == candidate_id]
    if exact:
        if len(exact) > 1:
            return {
                "status": "CONFLICT",
                "id": candidate_id,
                "name": candidate_name,
                "reason": f"canonical ID already appears in multiple files: {[row.path for row in exact]}",
            }
        existing = exact[0]
        if existing.type != candidate_type or _norm(existing.name) != _norm(candidate_name):
            return {
                "status": "CONFLICT",
                "id": candidate_id,
                "name": candidate_name,
                "path": existing.path,
                "reason": (
                    "exact canonical ID exists but type/name differs: "
                    f"existing=({existing.type}, {existing.name!r}) candidate=({candidate_type}, {candidate_name!r})"
                ),
            }
        return {
            "status": "REUSE",
            "id": candidate_id,
            "name": candidate_name,
            "path": existing.path,
            "reason": "exact canonical ID and identity fields match",
        }

    same_name = [
        row
        for row in canonical
        if row.type == candidate_type and _norm(row.name) == _norm(candidate_name)
    ]
    if same_name:
        return {
            "status": "CONFLICT",
            "id": candidate_id,
            "name": candidate_name,
            "candidates": [{"id": row.id, "path": row.path} for row in same_name],
            "reason": "same type/name exists under a different canonical ID; explicit identity decision required",
        }

    return {
        "status": "NEW",
        "id": candidate_id,
        "name": candidate_name,
        "reason": "no exact canonical ID or same-name identity candidate exists",
    }


def _promotion_exclusions(unit_id: str, root: Path = ROOT) -> list[dict[str, Any]]:
    matches = sorted((root / "research/promotions").glob(f"{unit_id}-*-promotion.yaml"))
    if not matches:
        return []
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one verified promotion for {unit_id}, found {len(matches)}")
    promotion = _load_yaml(matches[0]) or {}
    result: list[dict[str, Any]] = []
    for change in promotion.get("changes", []) or []:
        if not isinstance(change, dict):
            continue
        proposed = change.get("proposed_change") or {}
        action = proposed.get("action") if isinstance(proposed, dict) else None
        target = change.get("target") or {}
        if action not in {"manual_review", "remove_entry"}:
            continue
        result.append(
            {
                "finding_id": change.get("finding_id"),
                "section": target.get("section") if isinstance(target, dict) else None,
                "id": target.get("id") if isinstance(target, dict) else None,
                "action": action,
                "reason": proposed.get("reason") if isinstance(proposed, dict) else None,
                "human_decision": change.get("human_decision"),
            }
        )
    return result


def build_plan(unit_id: str, root: Path = ROOT) -> dict[str, Any]:
    unit_id = unit_id.upper()
    packet_file = _one(root / "research/packets", f"{unit_id}-*.yaml")
    packet = _load_yaml(packet_file)
    if not isinstance(packet, dict):
        raise RuntimeError(f"{packet_file} is not a YAML mapping")

    canonical = load_canonical_entities(root)
    entity_plan = [
        classify_entity(row, canonical)
        for row in packet.get("entities", []) or []
        if isinstance(row, dict)
    ]
    conflicts = [row for row in entity_plan if row["status"] == "CONFLICT"]

    exclusions = _promotion_exclusions(unit_id, root)
    excluded_assertion_ids = {
        row["id"] for row in exclusions if row.get("section") == "assertions" and row.get("id")
    }
    promotable_assertions = [
        str(row.get("id"))
        for row in packet.get("assertions", []) or []
        if isinstance(row, dict) and row.get("id") and str(row.get("id")) not in excluded_assertion_ids
    ]

    return {
        "research_unit_id": unit_id,
        "packet": str(packet_file.relative_to(root)),
        "entities": entity_plan,
        "assertions": {
            "promotable_packet_ids": promotable_assertions,
            "excluded_or_manual": exclusions,
        },
        "summary": {
            "NEW": sum(1 for row in entity_plan if row["status"] == "NEW"),
            "REUSE": sum(1 for row in entity_plan if row["status"] == "REUSE"),
            "CONFLICT": len(conflicts),
        },
        "blocked": bool(conflicts),
    }


def _print_plan(plan: dict[str, Any]) -> None:
    print(f"{plan['research_unit_id']} canonical promotion plan")
    print(f"packet: {plan['packet']}")
    print()
    print("Entities")
    for row in plan["entities"]:
        suffix = f"  {row.get('path', '')}" if row.get("path") else ""
        print(f"{row['status']:<8} {row['id']:<36} {row.get('name', '')}{suffix}")
        if row["status"] == "CONFLICT":
            print(f"         ! {row['reason']}")
    print()
    print("Assertions")
    print(f"PROMOTABLE {len(plan['assertions']['promotable_packet_ids'])}")
    for row in plan["assertions"]["excluded_or_manual"]:
        target = row.get("id") or "<no target id>"
        print(f"EXCLUDE    {target:<36} {row.get('action')}: {row.get('reason') or row.get('finding_id')}")
    summary = plan["summary"]
    print()
    print(f"Summary: NEW {summary['NEW']} / REUSE {summary['REUSE']} / CONFLICT {summary['CONFLICT']}")
    print("STOP: resolve canonical identity conflicts" if plan["blocked"] else "READY: canonical promotion plan has no identity conflicts")


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan canonical promotion without modifying repository data.")
    parser.add_argument("unit_id")
    parser.add_argument("--yaml", action="store_true", help="Emit the plan as YAML")
    args = parser.parse_args()
    plan = build_plan(args.unit_id)
    if args.yaml:
        print(yaml.safe_dump(plan, sort_keys=False, allow_unicode=True))
    else:
        _print_plan(plan)
    return 2 if plan["blocked"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
