from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_PERSPECTIVES = {"historical", "later_interpretation", "modern_abstraction"}
REVIEWED_STATUSES = {"historically_reviewed", "accepted", "published"}


def _load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _rows(directory: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.yaml")):
        data = _load_yaml(path) or []
        if isinstance(data, dict):
            data = [data]
        if isinstance(data, list):
            result.extend(row for row in data if isinstance(row, dict))
    return result


def _story(path: Path) -> dict[str, Any]:
    data = _load_yaml(path)
    if isinstance(data, list):
        if len(data) != 1 or not isinstance(data[0], dict):
            raise ValueError(f"{path} must contain exactly one Story mapping")
        return data[0]
    if isinstance(data, dict):
        return data
    raise ValueError(f"{path} does not contain a Story mapping")


def _source_ids(root: Path) -> set[str]:
    ids: set[str] = set()
    for row in _rows(root / "sources"):
        if row.get("id"):
            ids.add(str(row["id"]))
    return ids


def validate_story_evidence(path: Path, root: Path = ROOT) -> tuple[list[str], list[str]]:
    story = _story(path)
    errors: list[str] = []
    warnings: list[str] = []

    assertions = {
        str(row["id"]): row
        for row in _rows(root / "data/assertions")
        if row.get("id")
    }
    sources = _source_ids(root)

    steps = story.get("steps")
    if not isinstance(steps, list) or not steps:
        return ["Story has no steps"], warnings

    step_by_id: dict[str, dict[str, Any]] = {}
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            errors.append(f"step #{index} is not a mapping")
            continue
        step_id = str(step.get("id", "")).strip()
        if not step_id:
            errors.append(f"step #{index} is missing id")
            continue
        if step_id in step_by_id:
            errors.append(f"duplicate Story step id: {step_id}")
            continue
        step_by_id[step_id] = step

        narrative = str(step.get("narrative", "")).strip()
        refs = step.get("assertion_refs")
        if narrative and (not isinstance(refs, list) or not refs):
            errors.append(f"{step_id}: narrative has no assertion_refs")
            continue
        if not isinstance(refs, list):
            refs = []

        perspective = str(step.get("perspective", "")).strip()
        if perspective not in ALLOWED_PERSPECTIVES:
            errors.append(f"{step_id}: invalid or missing perspective {perspective!r}")

        resolved: list[dict[str, Any]] = []
        for ref in refs:
            assertion_id = str(ref)
            assertion = assertions.get(assertion_id)
            if assertion is None:
                errors.append(f"{step_id}: missing canonical assertion {assertion_id}")
                continue
            resolved.append(assertion)
            if assertion.get("status") not in REVIEWED_STATUSES:
                errors.append(
                    f"{step_id}: assertion {assertion_id} is not historically reviewed/accepted/published"
                )
            assertion_sources = assertion.get("sources")
            if not isinstance(assertion_sources, list) or not assertion_sources:
                errors.append(f"{step_id}: assertion {assertion_id} has no persistent sources")
                continue
            missing = sorted(str(src) for src in assertion_sources if str(src) not in sources)
            if missing:
                errors.append(f"{step_id}: assertion {assertion_id} has missing source refs {missing}")

        if resolved and perspective in ALLOWED_PERSPECTIVES:
            perspectives = {str(row.get("perspective", "")) for row in resolved}
            if perspective not in perspectives:
                errors.append(
                    f"{step_id}: no referenced assertion matches Story perspective {perspective}; "
                    f"found {sorted(perspectives)}"
                )

    links = story.get("links") or []
    if not isinstance(links, list):
        errors.append("Story links must be a list")
        links = []
    for index, link in enumerate(links, start=1):
        if not isinstance(link, dict):
            errors.append(f"link #{index} is not a mapping")
            continue
        source_id = str(link.get("from", ""))
        target_id = str(link.get("to", ""))
        link_type = str(link.get("type", ""))
        if source_id not in step_by_id or target_id not in step_by_id:
            errors.append(f"link #{index}: dangling endpoint {source_id!r} -> {target_id!r}")
            continue
        if link_type == "continues":
            source_refs = step_by_id[source_id].get("assertion_refs") or []
            target_refs = step_by_id[target_id].get("assertion_refs") or []
            source_sources = {
                str(src)
                for ref in source_refs
                for src in (assertions.get(str(ref), {}).get("sources") or [])
            }
            target_sources = {
                str(src)
                for ref in target_refs
                for src in (assertions.get(str(ref), {}).get("sources") or [])
            }
            if not source_refs or not target_refs:
                errors.append(
                    f"{source_id}->{target_id}: continues requires evidence-backed endpoint steps"
                )
            elif not (source_sources & target_sources):
                warnings.append(
                    f"{source_id}->{target_id}: continues has no shared persistent source across endpoint "
                    "assertions; Story Critic must explicitly verify direct continuity rather than chronology"
                )

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate Story-to-assertion-to-source evidence structure before Story Critic. "
            "This does not judge historical truth."
        )
    )
    parser.add_argument("story")
    parser.add_argument("--strict-warnings", action="store_true")
    args = parser.parse_args()

    path = Path(args.story)
    if not path.is_absolute():
        path = ROOT / path
    errors, warnings = validate_story_evidence(path)
    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings:
        print(f"WARNING: {item}")
    if errors:
        return 1
    if warnings and args.strict_warnings:
        return 2
    print(f"Story evidence gate passed: {path.relative_to(ROOT)}")
    if warnings:
        print(f"  {len(warnings)} strong-link warning(s) require Story Critic attention")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
