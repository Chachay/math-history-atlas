from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from scripts.common import ROOT, load_yaml_files


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_packet_ref(packet: dict[str, Any], ref: dict[str, Any]) -> bool:
    section = ref.get("section")
    if not section:
        return False
    rows: Any = packet
    for part in str(section).split("."):
        if not isinstance(rows, dict) or part not in rows:
            return False
        rows = rows[part]
    if not isinstance(rows, list):
        return False

    if ref.get("id"):
        return any(isinstance(row, dict) and row.get("id") == ref["id"] for row in rows)

    match = ref.get("match")
    if isinstance(match, dict):
        return any(
            isinstance(row, dict)
            and all(str(row.get(k)) == str(v) for k, v in match.items())
            for row in rows
        )
    return False


def validate_provenance() -> list[str]:
    errors: list[str] = []
    canonical_assertions = {
        row["id"]: row
        for row in load_yaml_files(ROOT / "data/assertions")
        if isinstance(row, dict) and row.get("id")
    }
    stories = {
        row["id"]: row
        for row in load_yaml_files(ROOT / "editorial/stories")
        if isinstance(row, dict) and row.get("id")
    }

    maps = sorted((ROOT / "research/promotions").glob("*-canonical-map.yaml"))
    for map_file in maps:
        mapping = load_yaml(map_file)
        if not isinstance(mapping, dict):
            errors.append(f"{map_file.name}: map is not a mapping")
            continue

        packet_value = mapping.get("packet")
        if not packet_value:
            errors.append(f"{map_file.name}: missing packet path")
            continue
        packet_file = ROOT / str(packet_value)
        if not packet_file.exists():
            errors.append(f"{map_file.name}: missing packet {packet_value}")
            continue
        packet = load_yaml(packet_file)
        if not isinstance(packet, dict):
            errors.append(f"{map_file.name}: packet is not a mapping")
            continue

        for row in mapping.get("canonical_assertions", []):
            canonical_id = row.get("canonical_id") if isinstance(row, dict) else None
            if canonical_id not in canonical_assertions:
                errors.append(f"{map_file.name}: unknown canonical assertion {canonical_id}")
                continue
            refs = row.get("packet_refs", [])
            if not refs:
                errors.append(f"{map_file.name}: {canonical_id} has no packet_refs")
            for ref in refs:
                if not isinstance(ref, dict) or not resolve_packet_ref(packet, ref):
                    errors.append(f"{map_file.name}: unresolved packet ref for {canonical_id}: {ref}")

        for story_row in mapping.get("stories", []):
            story_id = story_row.get("story_id") if isinstance(story_row, dict) else None
            story = stories.get(story_id)
            if story is None:
                errors.append(f"{map_file.name}: unknown story {story_id}")
                continue
            steps = {step.get("id"): step for step in story.get("steps", []) if isinstance(step, dict)}
            for mapped_step in story_row.get("steps", []):
                step_id = mapped_step.get("step_id") if isinstance(mapped_step, dict) else None
                step = steps.get(step_id)
                if step is None:
                    errors.append(f"{map_file.name}: unknown Story step {story_id}/{step_id}")
                    continue
                expected = list(mapped_step.get("canonical_assertion_refs", []))
                actual = list(step.get("assertion_refs", []))
                if expected != actual:
                    errors.append(
                        f"{map_file.name}: Story step {story_id}/{step_id} provenance differs "
                        f"from assertion_refs: map={expected}, story={actual}"
                    )

    return errors


def main() -> int:
    errors = validate_provenance()
    if errors:
        print("\n".join("ERROR: " + error for error in errors))
        return 1
    print("Promotion provenance validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
