from __future__ import annotations

import argparse
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _save(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )


def _one_by_unit(directory: Path, unit_id: str, *, story_review: bool = False) -> Path | None:
    matches: list[Path] = []
    for path in sorted(directory.glob("*.yaml")):
        data = _load(path) or {}
        if not isinstance(data, dict):
            continue
        header = data.get("review", {}) if story_review else data.get("review", {})
        if isinstance(header, dict) and str(header.get("research_unit_id", "")).upper() == unit_id:
            matches.append(path)
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one review for {unit_id} in {directory}, found {len(matches)}")
    return matches[0] if matches else None


def _promotion(unit_id: str, root: Path) -> dict[str, Any]:
    matches = sorted((root / "research/promotions").glob(f"{unit_id}-*-promotion.yaml"))
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one verified promotion for {unit_id}, found {len(matches)}")
    if not matches:
        return {}
    data = _load(matches[0]) or {}
    return data if isinstance(data, dict) else {}


def _norm(text: str) -> str:
    text = text.casefold().replace("–", "-").replace("—", "-")
    return " ".join(re.findall(r"[a-z0-9]+", text))


def _similar(a: str, b: str) -> float:
    na, nb = _norm(a), _norm(b)
    if not na or not nb:
        return 0.0
    aset, bset = set(na.split()), set(nb.split())
    jaccard = len(aset & bset) / max(1, len(aset | bset))
    sequence = SequenceMatcher(None, na, nb).ratio()
    return max(jaccard, sequence)


def _downstream_hints(unit_id: str, root: Path) -> list[str]:
    hints: list[str] = []
    promotion = _promotion(unit_id, root)
    for change in promotion.get("changes", []) or []:
        if not isinstance(change, dict):
            continue
        proposed = change.get("proposed_change") or {}
        target = change.get("target") or {}
        action = proposed.get("action") if isinstance(proposed, dict) else None
        if action not in {"remove", "remove_entry"}:
            continue
        if not isinstance(target, dict) or target.get("section") != "question_transitions":
            continue
        for key in ("reason",):
            if isinstance(proposed, dict) and proposed.get(key):
                hints.append(str(proposed[key]))
        if change.get("reason"):
            hints.append(str(change["reason"]))
        if change.get("needed_evidence"):
            hints.append(str(change["needed_evidence"]))
    review_path = _one_by_unit(root / "research/reviews", unit_id)
    if review_path:
        review = _load(review_path) or {}
        for finding in review.get("findings", []) or []:
            if not isinstance(finding, dict):
                continue
            target = finding.get("target") or finding.get("reviewed_item") or {}
            proposed = finding.get("proposed_change") or {}
            if (
                isinstance(target, dict)
                and target.get("section") == "question_transitions"
                and str(finding.get("classification", "")).upper() in {"REJECT", "WEAK_EVIDENCE"}
            ):
                hints.extend(
                    str(value)
                    for value in (finding.get("reason"), finding.get("needed_evidence"), proposed.get("reason") if isinstance(proposed, dict) else None)
                    if value
                )
    return hints


def _allocated_units(root: Path) -> list[str]:
    result: list[str] = []
    for path in sorted((root / "research/units").glob("R[0-9][0-9][0-9]-*.md")):
        result.append(path.name.split("-", 1)[0])
    return result


def _roadmap_files(root: Path) -> list[str]:
    return [str(path.relative_to(root)) for path in sorted((root / "research/units").glob("ROADMAP-*.md"))]


def _existing_gap_files(unit_id: str, root: Path) -> list[Path]:
    return sorted((root / "research/gaps").glob(f"{unit_id}-*.yaml"))


def _existing_gap_rows(unit_id: str, root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in _existing_gap_files(unit_id, root):
        data = _load(path) or {}
        if isinstance(data, dict) and isinstance(data.get("research_gaps"), list):
            rows.extend(row for row in data["research_gaps"] if isinstance(row, dict))
    return rows


def _kind_for_gap(gap: dict[str, Any], downstream_hints: list[str]) -> tuple[str, str]:
    text = " ".join(str(gap.get(key, "")) for key in ("question", "needed_evidence"))
    future_phrases = (
        "later bounded unit",
        "future unit",
        "later unit",
        "downstream",
        "research handoff",
        "later research",
    )
    if any(phrase in text.casefold() for phrase in future_phrases):
        return "candidate_future_unit", "Story Critic explicitly frames the gap as later-unit/downstream work"
    if any(_similar(text, hint) >= 0.32 for hint in downstream_hints):
        return "candidate_future_unit", "Matches a rejected/withheld downstream question transition"
    return "supplementary", "Unresolved evidence can be filled without allocating a new research unit"


def build_gap_plan(unit_id: str, root: Path = ROOT) -> dict[str, Any]:
    unit_id = unit_id.upper()
    story_review_path = _one_by_unit(root / "editorial/reviews", unit_id, story_review=True)
    research_review_path = _one_by_unit(root / "research/reviews", unit_id)
    if story_review_path:
        story_review = _load(story_review_path) or {}
        raw_gaps = story_review.get("research_gaps") or []
        source_label = str(story_review_path.relative_to(root))
    elif research_review_path:
        research_review = _load(research_review_path) or {}
        raw_gaps = research_review.get("research_gaps") or []
        source_label = str(research_review_path.relative_to(root))
    else:
        raw_gaps = []
        source_label = "<none>"

    downstream_hints = _downstream_hints(unit_id, root)
    existing = _existing_gap_rows(unit_id, root)
    proposals: list[dict[str, Any]] = []
    for index, gap in enumerate(raw_gaps, start=1):
        if not isinstance(gap, dict):
            continue
        question = str(gap.get("question", "")).strip()
        if not question:
            continue
        kind, rationale = _kind_for_gap(gap, downstream_hints)
        match = next(
            (
                row
                for row in existing
                if _similar(question, str(row.get("question", ""))) >= 0.48
            ),
            None,
        )
        proposal_id = str(gap.get("id") or f"gap-{unit_id.lower()}-proposal-{index:02d}")
        row: dict[str, Any] = {
            "proposal_id": proposal_id,
            "originating_unit": unit_id,
            "kind": kind,
            "question": question,
            "needed_evidence": str(gap.get("needed_evidence", "")).strip(),
            "classification_rationale": rationale,
            "source": source_label,
            "registered": bool(match),
            "registered_gap_id": match.get("id") if match else None,
        }
        if kind == "candidate_future_unit":
            row["candidate_id"] = re.sub(r"^gap-", "", proposal_id).replace("story-", "")
            row["roadmap_eligibility"] = "unassigned; requires current roadmap review"
        proposals.append(row)

    return {
        "research_unit_id": unit_id,
        "source_review": source_label,
        "roadmap_snapshot": {
            "allocated_unit_ids": _allocated_units(root),
            "roadmap_files": _roadmap_files(root),
            "rule": "candidate_future_unit proposals never allocate an R-number automatically",
        },
        "proposals": proposals,
        "summary": {
            "supplementary": sum(1 for row in proposals if row["kind"] == "supplementary"),
            "candidate_future_unit": sum(1 for row in proposals if row["kind"] == "candidate_future_unit"),
            "already_registered": sum(1 for row in proposals if row["registered"]),
        },
    }


def _persistent_row(proposal: dict[str, Any]) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": proposal["proposal_id"],
        "status": "open",
        "kind": proposal["kind"],
        "originating_unit": proposal["originating_unit"],
        "question": proposal["question"],
        "needed_evidence": proposal["needed_evidence"],
    }
    if proposal["kind"] == "candidate_future_unit":
        row["candidate_id"] = proposal["candidate_id"]
        row["roadmap_eligibility"] = proposal["roadmap_eligibility"]
    return row


def apply_gap_plan(plan: dict[str, Any], root: Path = ROOT) -> Path | None:
    unit_id = str(plan["research_unit_id"])
    missing = [row for row in plan["proposals"] if not row.get("registered")]
    if not missing:
        return None
    existing_files = _existing_gap_files(unit_id, root)
    if len(existing_files) > 1:
        raise RuntimeError(
            f"{unit_id} already has multiple gap registry files; merge manually before automatic registration"
        )
    path = existing_files[0] if existing_files else root / "research/gaps" / f"{unit_id}-followups.yaml"
    data = _load(path) if path.exists() else {"research_unit_id": unit_id, "research_gaps": []}
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} is not a gap registry mapping")
    rows = data.setdefault("research_gaps", [])
    if not isinstance(rows, list):
        raise RuntimeError(f"{path} research_gaps must be a list")
    for proposal in missing:
        rows.append(_persistent_row(proposal))
    _save(path, data)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Propose persistent research gaps after Story Critic without allocating future R-numbers."
    )
    parser.add_argument("unit_id")
    parser.add_argument("--yaml", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    plan = build_gap_plan(args.unit_id)
    if args.yaml:
        print(yaml.safe_dump(plan, sort_keys=False, allow_unicode=True))
    else:
        print(f"{plan['research_unit_id']} research-gap completion")
        for row in plan["proposals"]:
            status = "REGISTERED" if row["registered"] else "PROPOSE"
            print(f"{status:<10} {row['kind']:<22} {row['proposal_id']}")
            print(f"           {row['question']}")
            if row["kind"] == "candidate_future_unit":
                print(f"           roadmap: {row['roadmap_eligibility']}")
        summary = plan["summary"]
        print(
            f"Summary: supplementary {summary['supplementary']} / "
            f"candidate_future_unit {summary['candidate_future_unit']} / "
            f"already registered {summary['already_registered']}"
        )
    if args.apply:
        path = apply_gap_plan(plan)
        if path is None:
            print("No registration changes: all proposed gaps are already persistent")
        else:
            print(f"Registered gaps in {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
