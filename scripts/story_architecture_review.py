from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

from scripts.common import ROOT


ALLOWED_DIMENSIONS = {"entry", "question_path", "question_disposition", "overlap"}
ALLOWED_CLASSIFICATIONS = {"PASS", "REVISE", "WEAK_EVIDENCE", "REJECT"}
ALLOWED_DISPOSITIONS = {
    "opens",
    "continues",
    "branches",
    "answered_for_story",
    "handoff",
    "remains_open",
}
ALLOWED_GAP_KINDS = {"evidence", "entry_context", "coverage", "synthesis", "intersection"}
ALLOWED_BURDENS = {"none", "light", "medium", "full_research"}
ALLOWED_RESOLUTION_MODES = {
    "editorial_edit",
    "editorial_synthesis",
    "supplementary_research",
    "candidate_future_unit",
}


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


def _story_rows(path: Path) -> list[dict[str, Any]]:
    data = _load_yaml(path) or []
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict) and row.get("id")]


def load_stories(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    stories: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "editorial/stories").glob("*.yaml")):
        for row in _story_rows(path):
            story_id = str(row["id"])
            item = dict(row)
            item["_path"] = str(path.relative_to(root))
            stories[story_id] = item
    return stories


def load_question_ids(root: Path = ROOT) -> set[str]:
    ids: set[str] = set()
    for path in sorted((root / "data/questions").glob("*.yaml")):
        data = _load_yaml(path) or []
        if isinstance(data, dict):
            data = [data]
        if isinstance(data, list):
            for row in data:
                if isinstance(row, dict) and row.get("id"):
                    ids.add(str(row["id"]))
    return ids


def load_question_edges(
    question_ids: set[str],
    root: Path = ROOT,
) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for row in _rows(root / "data/assertions"):
        subject = str(row.get("subject", ""))
        obj = str(row.get("object", ""))
        if subject not in question_ids or obj not in question_ids:
            continue
        edges.append(
            {
                "assertion_id": str(row.get("id", "")),
                "subject": subject,
                "predicate": str(row.get("predicate", "")),
                "object": obj,
                "perspective": str(row.get("perspective", "")),
                "certainty": str(row.get("certainty", "")),
                "status": str(row.get("status", "")),
                "period": row.get("period"),
            }
        )
    return sorted(
        edges,
        key=lambda row: (
            row["subject"],
            row["object"],
            row["assertion_id"],
        ),
    )


def _as_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if item is not None]


def _year_from_step(step: dict[str, Any]) -> Any:
    anchor = step.get("temporal_anchor")
    if isinstance(anchor, dict):
        return anchor.get("from")
    return None


def _story_context(story: dict[str, Any], question_ids: set[str]) -> dict[str, Any]:
    steps = story.get("steps") if isinstance(story.get("steps"), list) else []
    first = next((step for step in steps if isinstance(step, dict)), {})
    question_steps = []
    all_refs: list[str] = []
    all_assertions: list[str] = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        ref = str(step.get("ref", "")).strip()
        if ref:
            all_refs.append(ref)
        all_assertions.extend(_as_strings(step.get("assertion_refs")))
        if ref in question_ids:
            question_steps.append(
                {
                    "step_id": str(step.get("id", "")),
                    "question_id": ref,
                    "role": str(step.get("role", "")),
                    "perspective": str(step.get("perspective", "")),
                    "from": _year_from_step(step),
                }
            )

    return {
        "story_id": str(story.get("id", "")),
        "path": story.get("_path"),
        "title": story.get("title"),
        "description": story.get("description"),
        "entry": {
            "step_id": str(first.get("id", "")),
            "ref": str(first.get("ref", "")),
            "role": str(first.get("role", "")),
            "perspective": str(first.get("perspective", "")),
            "from": _year_from_step(first),
        },
        "question_phases": _as_strings(story.get("question_phases")),
        "question_steps": question_steps,
        "step_refs": sorted(set(all_refs)),
        "assertion_refs": sorted(set(all_assertions)),
    }


def _edge_context_for_story(
    story: dict[str, Any],
    question_edges: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    phases = set(_as_strings(story.get("question_phases")))
    path_edges = [
        edge
        for edge in question_edges
        if edge["subject"] in phases and edge["object"] in phases
    ]
    neighbor_edges = [
        edge
        for edge in question_edges
        if (edge["subject"] in phases or edge["object"] in phases)
        and not (edge["subject"] in phases and edge["object"] in phases)
    ]
    return path_edges, neighbor_edges


def build_architecture_context(
    selected_story_ids: list[str] | None = None,
    root: Path = ROOT,
) -> dict[str, Any]:
    stories = load_stories(root)
    question_ids = load_question_ids(root)
    question_edges = load_question_edges(question_ids, root)
    if selected_story_ids:
        missing = sorted(set(selected_story_ids) - set(stories))
        if missing:
            raise ValueError(f"Unknown Story id(s): {missing}")
        selected = {story_id: stories[story_id] for story_id in selected_story_ids}
    else:
        selected = stories

    contexts = {}
    for story_id, story in selected.items():
        context = _story_context(story, question_ids)
        path_edges, neighbor_edges = _edge_context_for_story(story, question_edges)
        context["question_phase_edges"] = path_edges
        context["neighbor_question_edges"] = neighbor_edges
        contexts[story_id] = context

    all_contexts = {
        story_id: _story_context(story, question_ids)
        for story_id, story in stories.items()
    }

    overlaps: list[dict[str, Any]] = []
    selected_ids = set(selected)
    seen: set[tuple[str, str]] = set()
    for left_id in selected_ids:
        left = all_contexts[left_id]
        for right_id, right in all_contexts.items():
            if left_id == right_id:
                continue
            pair = tuple(sorted((left_id, right_id)))
            if pair in seen:
                continue
            if not (pair[0] in selected_ids or pair[1] in selected_ids):
                continue
            seen.add(pair)
            shared_questions = sorted(set(left["question_phases"]) & set(right["question_phases"]))
            shared_refs = sorted(set(left["step_refs"]) & set(right["step_refs"]))
            shared_assertions = sorted(set(left["assertion_refs"]) & set(right["assertion_refs"]))
            if shared_questions or shared_refs or shared_assertions:
                overlaps.append(
                    {
                        "stories": list(pair),
                        "shared_question_phases": shared_questions,
                        "shared_step_refs": shared_refs,
                        "shared_assertion_refs": shared_assertions,
                    }
                )

    return {
        "review_type": "story_architecture_context",
        "selected_story_ids": sorted(selected_ids),
        "stories": [contexts[story_id] for story_id in sorted(contexts)],
        "overlaps": sorted(overlaps, key=lambda row: tuple(row["stories"])),
        "notes": [
            "This context reports structure only; overlap is not itself a historical influence or causal relation.",
            "Question-to-Question Network edges are canonical assertions; inspect predicate, perspective, certainty, and status before using them as a narrative spine.",
            "Candidate Network edges remain hypotheses and must not be silently upgraded into reviewed Story transitions.",
            "A broad title does not imply an obligation to reconstruct all upstream history.",
        ],
    }


def validate_architecture_review(path: Path, root: Path = ROOT) -> list[str]:
    data = _load_yaml(path)
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Architecture review must be a mapping"]

    stories = load_stories(root)
    question_ids = load_question_ids(root)
    review = data.get("review")
    if not isinstance(review, dict):
        errors.append("missing review mapping")
    else:
        if review.get("type") != "story_architecture":
            errors.append("review.type must be story_architecture")
        scoped = _as_strings(review.get("stories"))
        for story_id in scoped:
            if story_id not in stories:
                errors.append(f"review references unknown Story {story_id}")

    findings = data.get("findings")
    if not isinstance(findings, list) or not findings:
        errors.append("findings must be a non-empty list")
        return errors

    seen_ids: set[str] = set()
    for index, finding in enumerate(findings, start=1):
        if not isinstance(finding, dict):
            errors.append(f"finding #{index} is not a mapping")
            continue
        finding_id = str(finding.get("id", "")).strip()
        if not finding_id:
            errors.append(f"finding #{index} missing id")
        elif finding_id in seen_ids:
            errors.append(f"duplicate finding id {finding_id}")
        else:
            seen_ids.add(finding_id)

        classification = str(finding.get("classification", ""))
        if classification not in ALLOWED_CLASSIFICATIONS:
            errors.append(f"{finding_id}: invalid classification {classification!r}")
        dimension = str(finding.get("dimension", ""))
        if dimension not in ALLOWED_DIMENSIONS:
            errors.append(f"{finding_id}: invalid dimension {dimension!r}")

        targets = _as_strings(finding.get("stories"))
        if not targets:
            errors.append(f"{finding_id}: findings must reference at least one Story")
        for story_id in targets:
            if story_id not in stories:
                errors.append(f"{finding_id}: unknown Story {story_id}")

        if not str(finding.get("reason", "")).strip():
            errors.append(f"{finding_id}: missing reason")

        dispositions = finding.get("question_dispositions") or []
        if not isinstance(dispositions, list):
            errors.append(f"{finding_id}: question_dispositions must be a list")
            dispositions = []
        for item in dispositions:
            if not isinstance(item, dict):
                errors.append(f"{finding_id}: invalid question_disposition row")
                continue
            question_id = str(item.get("question", ""))
            disposition = str(item.get("disposition", ""))
            if question_id not in question_ids:
                errors.append(f"{finding_id}: unknown Question {question_id}")
            if disposition not in ALLOWED_DISPOSITIONS:
                errors.append(f"{finding_id}: invalid disposition {disposition!r}")

        gap = finding.get("gap")
        if classification in {"REVISE", "WEAK_EVIDENCE", "REJECT"}:
            if not isinstance(gap, dict):
                errors.append(f"{finding_id}: non-PASS finding requires gap mapping")
                continue
            kind = str(gap.get("kind", ""))
            burden = str(gap.get("research_burden", ""))
            mode = str(gap.get("resolution_mode", ""))
            if kind not in ALLOWED_GAP_KINDS:
                errors.append(f"{finding_id}: invalid gap kind {kind!r}")
            if burden not in ALLOWED_BURDENS:
                errors.append(f"{finding_id}: invalid research_burden {burden!r}")
            if mode not in ALLOWED_RESOLUTION_MODES:
                errors.append(f"{finding_id}: invalid resolution_mode {mode!r}")
            if kind == "entry_context" and mode == "candidate_future_unit":
                errors.append(
                    f"{finding_id}: entry_context alone must not auto-escalate to candidate_future_unit"
                )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build structural context for Story Architecture Review or validate a persistent review artifact. "
            "The tool does not make historical or editorial judgments automatically."
        )
    )
    sub = parser.add_subparsers(dest="command", required=True)

    context_parser = sub.add_parser("context")
    context_parser.add_argument("story_ids", nargs="*")
    context_parser.add_argument("--output")

    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("review")

    args = parser.parse_args()
    if args.command == "context":
        context = build_architecture_context(args.story_ids or None)
        rendered = yaml.safe_dump(context, sort_keys=False, allow_unicode=True)
        if args.output:
            output = Path(args.output)
            if not output.is_absolute():
                output = ROOT / output
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(rendered, encoding="utf-8")
            print(output.relative_to(ROOT))
        else:
            print(rendered, end="")
        return 0

    review_path = Path(args.review)
    if not review_path.is_absolute():
        review_path = ROOT / review_path
    errors = validate_architecture_review(review_path)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print(f"Story Architecture Review valid: {review_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
