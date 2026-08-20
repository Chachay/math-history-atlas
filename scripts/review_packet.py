from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


REVIEWABLE_CLASSIFICATIONS = {
    "REJECT",
    "REVISE",
    "WEAK_EVIDENCE",
}


@dataclass
class ReviewItem:
    key: str
    kind: str
    item_id: str
    classification: str
    severity: str | None
    title: str
    critique: str
    needed_change: str | None
    evidence: list[dict[str, Any]]
    target: dict[str, Any] | None = None
    proposed_change: dict[str, Any] | None = None


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


def find_file(directory: Path, unit_id: str) -> Path:
    matches = sorted(directory.glob(f"{unit_id}-*.yaml"))

    if not matches:
        raise FileNotFoundError(
            f"No YAML file matching {unit_id}-*.yaml in {directory}"
        )

    if len(matches) > 1:
        names = ", ".join(str(p) for p in matches)
        raise RuntimeError(
            f"Multiple files match {unit_id} in {directory}: {names}"
        )

    return matches[0]


def short_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_findings(review: dict[str, Any]) -> list[ReviewItem]:
    items: list[ReviewItem] = []

    for index, row in enumerate(review.get("findings", []), start=1):
        item_id = short_text(row.get("id")) or f"finding-{index:03d}"

        reviewed_item = row.get("reviewed_item") or {}
        section = short_text(reviewed_item.get("section")) or "unknown"

        target = row.get("target") or reviewed_item

        items.append(
            ReviewItem(
                key=f"finding:{item_id}",
                kind=section.upper().replace("_", " "),
                item_id=item_id,
                classification=short_text(
                    row.get("classification")
                ).upper(),
                severity=short_text(row.get("severity")) or None,
                title=item_id,
                critique=short_text(row.get("reason")),
                needed_change=short_text(
                    row.get("needed_evidence")
                ) or None,
                evidence=row.get("evidence") or [],
                target=target or None,
                proposed_change=row.get("proposed_change"),
            )
        )

    return items

def normalize_global_findings(review: dict[str, Any]) -> list[ReviewItem]:
    items: list[ReviewItem] = []

    for row in review.get("critical_global_findings", []):
        item_id = short_text(row.get("id"))

        items.append(
            ReviewItem(
                key=f"global:{item_id}",
                kind="GLOBAL",
                item_id=item_id,
                classification=short_text(row.get("classification")).upper(),
                severity=short_text(row.get("severity")) or None,
                title=short_text(row.get("finding")),
                critique=short_text(row.get("finding")),
                needed_change=short_text(row.get("required_change")) or None,
                evidence=row.get("evidence") or [],
            )
        )

    return items


def normalize_chronology_reviews(review: dict[str, Any]) -> list[ReviewItem]:
    items: list[ReviewItem] = []

    for index, row in enumerate(review.get("chronology_reviews", []), start=1):
        date = short_text(row.get("date"))
        item_id = date or f"chronology-{index:03d}"

        items.append(
            ReviewItem(
                key=f"chronology:{item_id}",
                kind="CHRONOLOGY",
                item_id=item_id,
                classification=short_text(row.get("classification")).upper(),
                severity=None,
                title=date,
                critique=short_text(row.get("reason")),
                needed_change=short_text(row.get("needed_evidence")) or None,
                evidence=row.get("evidence") or [],
            )
        )

    return items


def normalize_assertion_reviews(review: dict[str, Any]) -> list[ReviewItem]:
    items: list[ReviewItem] = []

    for row in review.get("assertion_reviews", []):
        item_id = short_text(row.get("id"))

        items.append(
            ReviewItem(
                key=f"assertion:{item_id}",
                kind="ASSERTION",
                item_id=item_id,
                classification=short_text(row.get("classification")).upper(),
                severity=None,
                title=item_id,
                critique=short_text(row.get("reason")),
                needed_change=short_text(row.get("needed_evidence")) or None,
                evidence=row.get("evidence") or [],
            )
        )

    return items


def normalize_question_transition_reviews(
    review: dict[str, Any],
) -> list[ReviewItem]:
    items: list[ReviewItem] = []

    for row in review.get("question_transition_reviews", []):
        item_id = short_text(row.get("id"))

        items.append(
            ReviewItem(
                key=f"question_transition:{item_id}",
                kind="QUESTION TRANSITION",
                item_id=item_id,
                classification=short_text(row.get("classification")).upper(),
                severity=None,
                title=item_id,
                critique=short_text(row.get("reason")),
                needed_change=short_text(row.get("needed_evidence")) or None,
                evidence=row.get("evidence") or [],
            )
        )

    return items

def build_review_items(review: dict[str, Any]) -> list[ReviewItem]:
    # Current critic schema
    if "findings" in review:
        return normalize_findings(review)

    # Backward compatibility with earlier critic output
    return (
        normalize_global_findings(review)
        + normalize_chronology_reviews(review)
        + normalize_assertion_reviews(review)
        + normalize_question_transition_reviews(review)
    )

def source_index(
    packet: dict[str, Any],
    review: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}

    for source in packet.get("sources", []):
        source_id = source.get("id")
        if source_id:
            result[source_id] = source

    for source in review.get("sources", []):
        source_id = source.get("id")
        if source_id:
            result[source_id] = source

    return result


def print_rule(char: str = "-", width: int = 72) -> None:
    print(char * width)


def print_evidence(
    evidence: list[dict[str, Any]],
    sources: dict[str, dict[str, Any]],
) -> None:
    if not evidence:
        print("(none)")
        return

    for item in evidence:
        source_id = short_text(item.get("source_id"))
        locator = short_text(item.get("locator"))
        supports = item.get("supports")

        print(f"- {source_id}")

        source = sources.get(source_id)
        if source:
            author = short_text(source.get("author"))
            title = short_text(source.get("title"))
            url = short_text(source.get("url"))

            label_parts = [x for x in (author, title) if x]
            if label_parts:
                print(f"  {' — '.join(label_parts)}")

            if url:
                print(f"  {url}")

        if locator:
            print(f"  locator: {locator}")

        if supports:
            if isinstance(supports, list):
                supports_text = ", ".join(str(x) for x in supports)
            else:
                supports_text = str(supports)

            print(f"  supports: {supports_text}")


def display_item(
    item: ReviewItem,
    current: int,
    total: int,
    sources: dict[str, dict[str, Any]],
) -> None:
    print()
    print_rule("=")
    header = f"[{current}/{total}] {item.kind} · {item.classification}"

    if item.severity:
        header += f" · {item.severity.upper()}"

    print(header)
    print_rule("=")

    print(f"ID: {item.item_id}")

    if item.kind == "GLOBAL":
        print()
        print("Finding")
        print_rule()
        print(item.critique or "(none)")
    else:
        print()
        print("Critic")
        print_rule()
        print(item.critique or "(none)")

    if item.needed_change:
        print()
        print("Required change / needed evidence")
        print_rule()
        print(item.needed_change)

    if item.target:
        print()
        print("Target")
        print_rule()
        print(
            yaml.safe_dump(
                item.target,
                sort_keys=False,
                allow_unicode=True,
            ).rstrip()
        )

    if item.proposed_change:
        print()
        print("Proposed change")
        print_rule()
        print(
            yaml.safe_dump(
                item.proposed_change,
                sort_keys=False,
                allow_unicode=True,
            ).rstrip()
        )

    print()
    print("Evidence")
    print_rule()
    print_evidence(item.evidence, sources)

    print()
    print("[a] Accept critic")
    print("[k] Keep original / reject critic")
    print("[n] Accept with note")
    print("[s] Skip for now")
    print("[q] Save and quit")


def default_resolution(unit_id: str, packet_file: Path, review_file: Path) -> dict[str, Any]:
    return {
        "research_unit_id": unit_id,
        "packet": packet_file.name,
        "review": review_file.name,
        "decisions": [],
    }


def decision_index(resolution: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}

    for row in resolution.get("decisions", []):
        key = row.get("review_key")
        if key:
            result[key] = row

    return result


def record_decision(
    resolution: dict[str, Any],
    item: ReviewItem,
    decision: str,
    note: str | None = None,
) -> None:
    decisions = resolution.setdefault("decisions", [])

    existing = None
    for row in decisions:
        if row.get("review_key") == item.key:
            existing = row
            break

    value = {
        "review_key": item.key,
        "kind": item.kind.lower().replace(" ", "_"),
        "item_id": item.item_id,
        "critic_classification": item.classification,
        "decision": decision,
        "note": note,
    }

    if existing is None:
        decisions.append(value)
    else:
        existing.clear()
        existing.update(value)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Interactively review a historical research critic report."
    )
    parser.add_argument(
        "unit_id",
        help="Research unit ID, for example R001",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Include PASS items as well as flagged items.",
    )

    args = parser.parse_args()
    unit_id = args.unit_id.upper()

    root = Path(__file__).resolve().parents[1]

    packet_dir = root / "research" / "packets"
    review_dir = root / "research" / "reviews"
    resolution_dir = root / "research" / "resolutions"

    packet_file = find_file(packet_dir, unit_id)
    review_file = find_file(review_dir, unit_id)

    packet = load_yaml(packet_file)
    review = load_yaml(review_file)

    packet_unit_id = str(packet.get("research_unit", {}).get("id", "")).upper()
    review_unit_id = str(review.get("review", {}).get("research_unit_id", "")).upper()

    if packet_unit_id != unit_id:
        raise ValueError(
            f"Packet research unit is {packet_unit_id!r}, expected {unit_id!r}"
        )

    if review_unit_id != unit_id:
        raise ValueError(
            f"Review research unit is {review_unit_id!r}, expected {unit_id!r}"
        )

    resolution_file = (
        resolution_dir
        / packet_file.name.replace(".yaml", "-resolution.yaml")
    )

    if resolution_file.exists():
        resolution = load_yaml(resolution_file)
    else:
        resolution = default_resolution(unit_id, packet_file, review_file)

    sources = source_index(packet, review)
    all_items = build_review_items(review)

    if args.all:
        queue = all_items
    else:
        queue = [
            item
            for item in all_items
            if item.classification in REVIEWABLE_CLASSIFICATIONS
        ]

    decisions = decision_index(resolution)

    remaining = [
        item
        for item in queue
        if item.key not in decisions
    ]

    title = packet.get("research_unit", {}).get("title", "")

    print()
    print(f"{unit_id} — {title}")
    print_rule("=")
    print(f"Reviewable items: {len(queue)}")
    print(f"Resolved:         {len(queue) - len(remaining)}")
    print(f"Remaining:        {len(remaining)}")

    if not remaining:
        print()
        print("No unresolved review items.")
        print(f"Resolution file: {resolution_file.relative_to(root)}")
        return 0

    total = len(remaining)

    for index, item in enumerate(remaining, start=1):
        while True:
            display_item(item, index, total, sources)

            choice = input("\n> ").strip().lower()

            if choice == "a":
                record_decision(
                    resolution,
                    item,
                    decision="accept_critic",
                )
                save_yaml(resolution_file, resolution)
                break

            if choice == "k":
                record_decision(
                    resolution,
                    item,
                    decision="keep_original",
                )
                save_yaml(resolution_file, resolution)
                break

            if choice == "n":
                note = input("Note: ").strip()

                record_decision(
                    resolution,
                    item,
                    decision="accept_critic_with_note",
                    note=note or None,
                )
                save_yaml(resolution_file, resolution)
                break

            if choice == "s":
                break

            if choice == "q":
                save_yaml(resolution_file, resolution)

                print()
                print(
                    f"Saved: {resolution_file.relative_to(root)}"
                )
                return 0

            print("Unknown command. Use a, k, n, s, or q.")

    save_yaml(resolution_file, resolution)

    print()
    print_rule("=")
    print("Review complete.")
    print(f"Saved: {resolution_file.relative_to(root)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
