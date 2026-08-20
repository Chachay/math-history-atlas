from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


ACCEPTED_DECISIONS = {
    "accept_critic",
    "accept_critic_with_note",
}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"{path} does not contain a YAML mapping.")

    return data


def save_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="\n") as f:
        yaml.safe_dump(
            data,
            f,
            sort_keys=False,
            allow_unicode=True,
            width=100,
        )


def find_file(directory: Path, unit_id: str, suffix: str = "") -> Path:
    pattern = f"{unit_id}-*{suffix}.yaml"
    matches = sorted(directory.glob(pattern))

    if not matches:
        raise FileNotFoundError(
            f"No YAML file matching {pattern} in {directory}"
        )

    if len(matches) > 1:
        names = ", ".join(str(p) for p in matches)
        raise RuntimeError(
            f"Multiple files match {pattern} in {directory}: {names}"
        )

    return matches[0]


def index_findings(review: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}

    for row in review.get("findings", []):
        finding_id = row.get("id")
        if finding_id:
            result[str(finding_id)] = row

    return result


def build_promotion(
    unit_id: str,
    packet_file: Path,
    review_file: Path,
    resolution_file: Path,
    review: dict[str, Any],
    resolution: dict[str, Any],
) -> dict[str, Any]:
    findings = index_findings(review)

    changes: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for decision in resolution.get("decisions", []):
        decision_value = decision.get("decision")

        if decision_value not in ACCEPTED_DECISIONS:
            continue

        item_id = str(decision.get("item_id", "")).strip()
        finding = findings.get(item_id)

        if finding is None:
            skipped.append(
                {
                    "item_id": item_id,
                    "reason": "finding_not_found_in_current_review",
                }
            )
            continue

        target = finding.get("target")
        proposed_change = finding.get("proposed_change")

        if not target:
            skipped.append(
                {
                    "item_id": item_id,
                    "reason": "missing_target",
                }
            )
            continue

        if not proposed_change:
            skipped.append(
                {
                    "item_id": item_id,
                    "reason": "missing_proposed_change",
                }
            )
            continue

        action = proposed_change.get("action")

        if not action:
            skipped.append(
                {
                    "item_id": item_id,
                    "reason": "missing_proposed_change_action",
                }
            )
            continue

        changes.append(
            {
                "finding_id": item_id,
                "critic_classification": finding.get("classification"),
                "human_decision": decision_value,
                "human_note": decision.get("note"),
                "target": target,
                "proposed_change": proposed_change,
                "status": "proposed",
            }
        )

    return {
        "research_unit_id": unit_id,
        "packet": packet_file.name,
        "review": review_file.name,
        "resolution": resolution_file.name,
        "summary": {
            "proposed_changes": len(changes),
            "skipped_items": len(skipped),
        },
        "changes": changes,
        "skipped": skipped,
    }


def resolve_section(
    packet: dict[str, Any],
    section_path: str,
) -> list[Any]:
    current: Any = packet

    for part in section_path.split("."):
        if not isinstance(current, dict):
            raise ValueError(
                f"Cannot resolve section path {section_path!r}: "
                f"{part!r} is below a non-mapping object."
            )

        if part not in current:
            raise ValueError(
                f"Section path {section_path!r} does not exist "
                f"in the Research Packet."
            )

        current = current[part]

    if not isinstance(current, list):
        raise ValueError(
            f"Target section {section_path!r} is not a list in the packet."
        )

    return current


def match_target(
    packet: dict[str, Any],
    target: dict[str, Any],
) -> tuple[str, list[Any], list[int]]:
    section = target.get("section")

    if not section:
        raise ValueError("Target is missing 'section'.")

    rows = resolve_section(packet, section)
    matches: list[int] = []

    target_id = target.get("id")
    target_match = target.get("match")

    if target_id:
        for index, row in enumerate(rows):
            if isinstance(row, dict) and row.get("id") == target_id:
                matches.append(index)

    elif isinstance(target_match, dict):
        if set(target_match.keys()) == {"contains"}:
            needle = str(target_match["contains"])

            for index, row in enumerate(rows):
                if isinstance(row, str) and needle in row:
                    matches.append(index)

        else:
            for index, row in enumerate(rows):
                if not isinstance(row, dict):
                    continue

                if all(
                    str(row.get(key)) == str(value)
                    for key, value in target_match.items()
                ):
                    matches.append(index)

    else:
        raise ValueError(
            f"Target for section {section!r} has neither 'id' nor 'match'."
        )

    return section, rows, matches


def source_index(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}

    for source in data.get("sources", []):
        if not isinstance(source, dict):
            continue
        source_id = source.get("id")
        if source_id:
            result[str(source_id)] = source

    return result


def apply_change(
    packet: dict[str, Any],
    review: dict[str, Any],
    change: dict[str, Any],
) -> str:
    target = change["target"]
    proposed_change = change["proposed_change"]
    action = proposed_change.get("action")

    section, rows, matches = match_target(packet, target)

    if len(matches) == 0:
        raise RuntimeError(
            f"{change['finding_id']}: target matched 0 objects."
        )

    if len(matches) > 1:
        raise RuntimeError(
            f"{change['finding_id']}: target matched "
            f"{len(matches)} objects; refusing automatic application."
        )

    index = matches[0]
    current = rows[index]

    if action == "replace_fields":
        if not isinstance(current, dict):
            raise RuntimeError(
                f"{change['finding_id']}: replace_fields target is not a mapping."
            )

        fields = proposed_change.get("fields")
        if not isinstance(fields, dict):
            raise ValueError(
                f"{change['finding_id']}: replace_fields requires 'fields'."
            )

        current.update(fields)
        return "applied"

    if action == "replace_entry":
        if "value" not in proposed_change:
            raise ValueError(
                f"{change['finding_id']}: replace_entry requires 'value'."
            )

        rows[index] = proposed_change["value"]
        return "applied"

    if action == "remove":
        del rows[index]
        return "applied"

    if action == "add_evidence":
        if not isinstance(current, dict):
            raise RuntimeError(
                f"{change['finding_id']}: add_evidence target is not a mapping."
            )

        requested_sources = proposed_change.get("sources")
        if not isinstance(requested_sources, list) or not requested_sources:
            raise ValueError(
                f"{change['finding_id']}: add_evidence requires a non-empty 'sources' list."
            )

        target_sources = current.setdefault("sources", [])
        if not isinstance(target_sources, list):
            raise RuntimeError(
                f"{change['finding_id']}: target 'sources' field is not a list."
            )

        packet_sources = packet.setdefault("sources", [])
        if not isinstance(packet_sources, list):
            raise RuntimeError("Packet 'sources' section is not a list.")

        packet_source_map = source_index(packet)
        review_source_map = source_index(review)

        for source_id_raw in requested_sources:
            source_id = str(source_id_raw)

            if source_id not in packet_source_map:
                source_record = review_source_map.get(source_id)
                if source_record is None:
                    raise RuntimeError(
                        f"{change['finding_id']}: source {source_id!r} is absent "
                        "from both packet and review source records."
                    )

                copied_source = deepcopy(source_record)
                packet_sources.append(copied_source)
                packet_source_map[source_id] = copied_source

            if source_id not in target_sources:
                target_sources.append(source_id)

        return "applied"

    if action == "manual_review":
        return "manual_review"

    return "unsupported"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build a promotion proposal from a Research Packet, "
            "Critic Review, and Human Resolution."
        )
    )
    parser.add_argument(
        "unit_id",
        help="Research unit ID, for example R001",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply safe accepted changes directly to the Research Packet.",
    )

    args = parser.parse_args()
    unit_id = args.unit_id.upper()

    root = Path(__file__).resolve().parents[1]

    packet_dir = root / "research" / "packets"
    review_dir = root / "research" / "reviews"
    resolution_dir = root / "research" / "resolutions"
    promotion_dir = root / "research" / "promotions"

    packet_file = find_file(packet_dir, unit_id)
    review_file = find_file(review_dir, unit_id)

    resolution_matches = sorted(
        p
        for p in resolution_dir.glob(f"{unit_id}-*-resolution.yaml")
        if "-v" not in p.stem
    )

    if not resolution_matches:
        raise FileNotFoundError(
            f"No current resolution file found for {unit_id}"
        )

    if len(resolution_matches) > 1:
        names = ", ".join(str(p) for p in resolution_matches)
        raise RuntimeError(
            f"Multiple current resolution files found: {names}"
        )

    resolution_file = resolution_matches[0]

    packet = load_yaml(packet_file)
    review = load_yaml(review_file)
    resolution = load_yaml(resolution_file)

    packet_unit_id = str(
        packet.get("research_unit", {}).get("id", "")
    ).upper()
    review_unit_id = str(
        review.get("review", {}).get("research_unit_id", "")
    ).upper()
    resolution_unit_id = str(
        resolution.get("research_unit_id", "")
    ).upper()

    if packet_unit_id != unit_id:
        raise ValueError(
            f"Packet unit ID is {packet_unit_id!r}, expected {unit_id!r}"
        )

    if review_unit_id != unit_id:
        raise ValueError(
            f"Review unit ID is {review_unit_id!r}, expected {unit_id!r}"
        )

    if resolution_unit_id != unit_id:
        raise ValueError(
            f"Resolution unit ID is {resolution_unit_id!r}, expected {unit_id!r}"
        )

    promotion = build_promotion(
        unit_id=unit_id,
        packet_file=packet_file,
        review_file=review_file,
        resolution_file=resolution_file,
        review=review,
        resolution=resolution,
    )

    promotion_file = (
        promotion_dir
        / packet_file.name.replace(".yaml", "-promotion.yaml")
    )

    save_yaml(promotion_file, promotion)

    print()
    print(f"{unit_id} promotion proposal")
    print("=" * 72)
    print(
        f"Proposed changes: {promotion['summary']['proposed_changes']}"
    )
    print(
        f"Skipped items:    {promotion['summary']['skipped_items']}"
    )
    print()
    print(f"Saved: {promotion_file.relative_to(root)}")

    if promotion["skipped"]:
        print()
        print("Skipped:")
        for item in promotion["skipped"]:
            print(f"- {item['item_id']}: {item['reason']}")

    if not args.apply:
        return 0

    applied = 0
    manual_review = 0
    unsupported = 0

    print()
    print("Applying accepted changes")
    print("=" * 72)

    for change in promotion["changes"]:
        action = change["proposed_change"].get("action")
        result = apply_change(packet, review, change)

        print(
            f"- {change['finding_id']}: "
            f"{action} -> {result}"
        )

        if result == "applied":
            applied += 1
        elif result == "manual_review":
            manual_review += 1
        else:
            unsupported += 1

    if applied:
        save_yaml(packet_file, packet)

    print()
    print(f"Applied changes: {applied}")
    print(f"Manual review:   {manual_review}")
    print(f"Unsupported:     {unsupported}")

    if applied:
        print()
        print(f"Updated: {packet_file.relative_to(root)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
