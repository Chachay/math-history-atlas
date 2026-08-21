from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

from scripts.integrity import require_integrity_match
from scripts.research_validation import (
    validate_packet,
    validate_resolution_semantics,
    validate_review,
)


ROOT = Path(__file__).resolve().parents[1]


def _one(directory: Path, pattern: str) -> Path | None:
    matches = sorted(directory.glob(pattern))
    if not matches:
        return None
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one {pattern} in {directory}, found {len(matches)}")
    return matches[0]


def _load(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} does not contain a YAML mapping")
    return data


def _mark(ok: bool) -> str:
    return "✓" if ok else "—"


def collect_status(unit_id: str) -> tuple[list[str], bool]:
    unit_id = unit_id.upper()
    lines = [unit_id]
    structurally_invalid = False

    brief = _one(ROOT / "research/units", f"{unit_id}-*.md")
    packet_file = _one(ROOT / "research/packets", f"{unit_id}-*.yaml")
    review_file = _one(ROOT / "research/reviews", f"{unit_id}-*.yaml")
    resolution_file = _one(ROOT / "research/resolutions", f"{unit_id}-*-resolution.yaml")
    promotion_file = _one(ROOT / "research/promotions", f"{unit_id}-*-promotion.yaml")
    canonical_map = _one(ROOT / "research/promotions", f"{unit_id}-*-canonical-map.yaml")

    packet = _load(packet_file)
    review = _load(review_file)
    resolution = _load(resolution_file)

    lines.append(f"Brief       {_mark(brief is not None)}")

    packet_valid = False
    if packet is not None:
        errors = validate_packet(packet)
        packet_valid = not errors
        if errors:
            structurally_invalid = True
            lines.append(f"Packet      ✗ {len(errors)} validation error(s)")
        else:
            lines.append("Packet      ✓ valid")
    else:
        lines.append("Packet      —")

    review_valid = False
    if review is not None and packet is not None:
        errors = validate_review(review, packet)
        review_valid = not errors
        if errors:
            structurally_invalid = True
            lines.append(f"Critic      ✗ {len(errors)} validation error(s)")
        else:
            findings = review.get("findings", [])
            counts: dict[str, int] = {}
            for row in findings:
                if isinstance(row, dict):
                    key = str(row.get("classification", "UNKNOWN"))
                    counts[key] = counts.get(key, 0) + 1
            summary = " / ".join(f"{key} {counts[key]}" for key in ("PASS", "REVISE", "WEAK_EVIDENCE", "REJECT") if key in counts)
            lines.append(f"Critic      ✓ {summary or 'reviewed'}")
    elif review is not None:
        structurally_invalid = True
        lines.append("Critic      ✗ packet missing")
    else:
        lines.append("Critic      —")

    resolution_valid = False
    integrity_bound = False
    if resolution is not None and packet is not None and review is not None:
        errors = validate_resolution_semantics(packet, review, resolution)
        resolution_valid = not errors
        if errors:
            structurally_invalid = True
            lines.append(f"Resolution  ✗ {len(errors)} semantic error(s)")
        else:
            lines.append("Resolution  ✓ material findings resolved")
            try:
                require_integrity_match(
                    resolution.get("integrity"),
                    packet,
                    review,
                    artifact_name=resolution_file.name if resolution_file else "resolution",
                )
            except RuntimeError:
                lines.append("Integrity   — not bound/current")
            else:
                integrity_bound = True
                lines.append("Integrity   ✓ fingerprints current")
    elif resolution is not None:
        structurally_invalid = True
        lines.append("Resolution  ✗ packet/review missing")
    elif review_valid:
        lines.append("Resolution  — WAITING HUMAN")
        lines.append("Integrity   —")
    else:
        lines.append("Resolution  —")
        lines.append("Integrity   —")

    lines.append(f"Promotion   {_mark(promotion_file is not None and integrity_bound)}")
    lines.append(f"Canonical   {_mark(canonical_map is not None)}")

    story_ids: list[str] = []
    if canonical_map is not None:
        mapping = _load(canonical_map) or {}
        for row in mapping.get("stories", []) or []:
            if isinstance(row, dict) and row.get("story_id"):
                story_ids.append(str(row["story_id"]))

    story_files = list((ROOT / "editorial/stories").glob("*.yaml"))
    story_review_files = list((ROOT / "editorial/reviews").glob("*.yaml"))
    story_found = False
    story_review_found = False
    if story_ids:
        for path in story_files:
            text = path.read_text(encoding="utf-8")
            story_found = story_found or any(story_id in text for story_id in story_ids)
        for path in story_review_files:
            text = path.read_text(encoding="utf-8")
            story_review_found = story_review_found or any(story_id in text for story_id in story_ids)
    lines.append(f"Story       {_mark(story_found)}")
    lines.append(f"StoryCritic {_mark(story_review_found)}")

    gap_dir = ROOT / "research/gaps"
    gap_found = False
    if gap_dir.exists():
        for path in gap_dir.glob("*.yaml"):
            if unit_id in path.read_text(encoding="utf-8"):
                gap_found = True
                break
    lines.append(f"Gaps        {_mark(gap_found)}")

    if structurally_invalid:
        lines.append("STOP: structurally invalid state")
    elif review_valid and resolution is None:
        lines.append("STOP: human resolution required")
    elif resolution_valid and not integrity_bound:
        lines.append("NEXT: bind resolution")
    elif integrity_bound and canonical_map is None:
        lines.append("NEXT: verified/canonical promotion")
    elif canonical_map is not None and not story_found:
        lines.append("NEXT: Story draft")
    elif story_found and not story_review_found:
        lines.append("NEXT: Story Critic")
    elif story_review_found:
        lines.append("READY: validation / mobile review")
    else:
        lines.append("NEXT: continue research unit")

    return lines, structurally_invalid


def main() -> int:
    parser = argparse.ArgumentParser(description="Report read-only research-unit workflow status.")
    parser.add_argument("unit_id")
    args = parser.parse_args()
    lines, invalid = collect_status(args.unit_id)
    print("\n".join(lines))
    return 1 if invalid else 0


if __name__ == "__main__":
    raise SystemExit(main())
