from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

from scripts.integrity import require_integrity_match, validate_finding_ids


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} does not contain a YAML mapping.")
    return data


def one(directory: Path, pattern: str) -> Path:
    matches = sorted(directory.glob(pattern))
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one {pattern} in {directory}, found {len(matches)}")
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify packet/review/resolution integrity, then run promote_packet.py."
    )
    parser.add_argument("unit_id")
    parser.add_argument("--apply", action="store_true")
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
    require_integrity_match(
        resolution.get("integrity"),
        packet,
        review,
        artifact_name=resolution_file.name,
    )

    if resolution.get("packet") != packet_file.name or resolution.get("review") != review_file.name:
        raise RuntimeError("Resolution file names do not match the current packet/review.")

    command = [sys.executable, str(root / "scripts/promote_packet.py"), unit_id]
    if args.apply:
        command.append("--apply")
    return subprocess.call(command, cwd=root)


if __name__ == "__main__":
    raise SystemExit(main())
