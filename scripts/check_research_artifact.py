from __future__ import annotations

import argparse
from pathlib import Path

from scripts.research_validation import (
    load_yaml_mapping,
    require_no_errors,
    validate_packet,
    validate_review,
)


def _find_packet_for_review(root: Path, review: dict) -> Path:
    unit_id = str(review.get("review", {}).get("research_unit_id", "")).upper()
    matches = sorted((root / "research/packets").glob(f"{unit_id}-*.yaml"))
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one packet for {unit_id}, found {len(matches)}")
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Research Packet or Historical Critic artifact.")
    parser.add_argument("path")
    args = parser.parse_args()

    path = Path(args.path).resolve()
    root = Path(__file__).resolve().parents[1]
    data = load_yaml_mapping(path)

    if "research_unit" in data:
        errors = validate_packet(data)
        label = "Research Packet"
    elif "review" in data and "findings" in data:
        packet = load_yaml_mapping(_find_packet_for_review(root, data))
        errors = validate_packet(packet) + validate_review(data, packet)
        label = "Historical Critic Review"
    else:
        raise RuntimeError("Artifact is neither a Research Packet nor a Historical Critic Review.")

    require_no_errors(errors, label=label)
    print(f"OK: {path.relative_to(root) if path.is_relative_to(root) else path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
