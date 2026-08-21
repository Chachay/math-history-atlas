from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

from scripts.integrity import artifact_integrity, validate_finding_ids
from scripts.research_validation import (
    require_no_errors,
    validate_packet,
    validate_resolution_semantics,
    validate_review,
)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} does not contain a YAML mapping.")
    return data


def save_yaml(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True, width=100)


def one(directory: Path, pattern: str) -> Path:
    matches = sorted(directory.glob(pattern))
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one {pattern} in {directory}, found {len(matches)}")
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and bind a human resolution to exact packet/review content hashes."
    )
    parser.add_argument("unit_id")
    args = parser.parse_args()
    unit_id = args.unit_id.upper()

    root = Path(__file__).resolve().parents[1]
    packet_file = one(root / "research/packets", f"{unit_id}-*.yaml")
    review_file = one(root / "research/reviews", f"{unit_id}-*.yaml")
    resolution_file = one(root / "research/resolutions", f"{unit_id}-*-resolution.yaml")

    packet = load_yaml(packet_file)
    review = load_yaml(review_file)
    resolution = load_yaml(resolution_file)

    validate_finding_ids(review)

    packet_unit = str(packet.get("research_unit", {}).get("id", "")).upper()
    review_unit = str(review.get("review", {}).get("research_unit_id", "")).upper()
    resolution_unit = str(resolution.get("research_unit_id", "")).upper()
    if {packet_unit, review_unit, resolution_unit} != {unit_id}:
        raise RuntimeError(
            f"Unit mismatch: packet={packet_unit}, review={review_unit}, resolution={resolution_unit}"
        )

    errors = validate_packet(packet)
    errors.extend(validate_review(review, packet))
    errors.extend(validate_resolution_semantics(packet, review, resolution))
    require_no_errors(errors, label=f"{unit_id} pre-bind")

    resolution["packet"] = packet_file.name
    resolution["review"] = review_file.name
    resolution["integrity"] = artifact_integrity(packet, review)
    save_yaml(resolution_file, resolution)

    print(f"Bound {resolution_file.relative_to(root)}")
    print(f"  packet: {resolution['integrity']['packet_sha256']}")
    print(f"  review: {resolution['integrity']['review_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
