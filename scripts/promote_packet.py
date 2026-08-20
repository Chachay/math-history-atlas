from __future__ import annotations

import argparse
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


def match_target(
    packet: dict[str, Any],
    target: dict[str, Any],
) -> tuple[str, list[int]]:
    section = target.get("section")

    if not section:
        raise ValueError("Target is missing 'section'.")

    rows = packet.get(section)

    if not isinstance(rows, list):
        raise ValueError(
            f"Target section {section!r} is not a list in the packet."
        )

    matches: list[int] = []

    target_id = target.get("id")
    target_match = target.get("match")

    if target_id:
        for index, row in enumerate(rows):
            if isinstance(row, dict) and row.get("id") == target_id:
                matches.append(index)

    elif isinstance(target_match, dict):
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

    return section, matches

def apply_change(
    packet: dict[str, Any],
    change: dict[str, Any],
) -> str:
    target = change["target"]
    proposed_change = change["proposed_change"]

    action = proposed_change.get("action")

    section, matches = match_target(packet, target)

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
    rows = packet[section]
    current = rows[index]

    if not isinstance(current, dict):
        raise RuntimeError(
            f"{change['finding_id']}: target object is not a mapping."
        )

    if action == "replace_fields":
        fields = proposed_change.get("fields")

        if not isinstance(fields, dict):
            raise ValueError(
                f"{change['finding_id']}: replace_fields requires 'fields'."
            )

        current.update(fields)
        return "applied"

    if action == "replace_entry":
        value = proposed_change.get("value")

        if not isinstance(value, dict):
            raise ValueError(
                f"{change['finding_id']}: replace_entry requires 'value'."
            )

        rows[index] = value
        return "applied"

    if action == "remove":
        del rows[index]
        return "applied"

    if action == "manual_review":
        return "manual_review"

    if action == "add_evidence":
        return "unsupported"

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
            print(
                f"- {item['item_id']}: {item['reason']}"
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
            print(
                f"- {item['item_id']}: {item['reason']}"
            )

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
