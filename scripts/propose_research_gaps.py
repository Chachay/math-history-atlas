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
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")


def _one_review(directory: Path, unit_id: str) -> Path | None:
    matches: list[Path] = []
    for path in sorted(directory.glob("*.yaml")):
        data = _load(path) or {}
        header = data.get("review", {}) if isinstance(data, dict) else {}
        if isinstance(header, dict) and str(header.get("research_unit_id", "")).upper() == unit_id:
            matches.append(path)
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one review for {unit_id} in {directory}, found {len(matches)}")
    return matches[0] if matches else None


def _promotion(unit_id: str, root: Path) -> dict[str, Any]:
    matches = sorted((root / "research/promotions").glob(f"{unit_id}-*-promotion.yaml"))
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one verified promotion for {unit_id}, found {len(matches)}")
    data = _load(matches[0]) if matches else {}
    return data if isinstance(data, dict) else {}


def _norm(text: str) -> str:
    text = text.casefold().replace("–", "-").replace("—", "-")
    return " ".join(re.findall(r"[a-z0-9]+", text))


def _similar(a: str, b: str) -> float:
    na, nb = _norm(a), _norm(b)
    if not na or not nb:
        return 0.0
    aset, bset = set(na.split()), set(nb.split())
    return max(
        len(aset & bset) / max(1, len(aset | bset)),
        SequenceMatcher(None, na, nb).ratio(),
    )


def _semantic_id_tokens(value: str) -> set[str]:
    ignored = {"gap", "story", "research", "unit"}
    return {
        token
        for token in re.findall(r"[a-z0-9]+", value.casefold())
        if token not in ignored and not re.fullmatch(r"r[0-9]+", token)
    }


def _same_gap(proposal_id: str, question: str, existing: dict[str, Any]) -> bool:
    existing_question = str(existing.get("question", ""))
    if _similar(question, existing_question) >= 0.38:
        return True
    left = _semantic_id_tokens(proposal_id)
    right = _semantic_id_tokens(str(existing.get("id", "")))
    if not left or not right:
        return False
    overlap = len(left & right) / max(1, min(len(left), len(right)))
    return overlap >= 0.5


def _downstream_hints(unit_id: str, root: Path) -> list[str]:
    hints: list[str] = []
    promotion = _promotion(unit_id, root)
    for change in promotion.get("changes", []) or []:
        if not isinstance(change, dict):
            continue
        proposed = change.get("proposed_change") or {}
        target = change.get("target") or {}
        action = proposed.get("action") if isinstance(proposed, dict) else None
        if action in {"remove", "remove_entry"} and isinstance(target, dict) and target.get("section") == "question_transitions":
            hints.extend(str(value) for value in (change.get("reason"), change.get("needed_evidence"), proposed.get("reason") if isinstance(proposed, dict) else None) if value)

    review_path = _one_review(root / "research/reviews", unit_id)
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
                hints.extend(str(value) for value in (finding.get("reason"), finding.get("needed_evidence"), proposed.get("reason") if isinstance(proposed, dict) else None) if value)
    return hints


def _allocated_units(root: Path) -> list[str]:
    return [path.name.split("-", 1)[0] for path in sorted((root / "research/units").glob("R[0-9][0-9][0-9]-*.md"))]


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
    lower = text.casefold()
    explicit_future_phrases = (
        "later bounded unit",
        "future unit",
        "later unit",
        "downstream",
        "research handoff",
        "later research",
    )
    future_spine_markers = (
        "1873",
        "1874",
        "set theory",
        "transfinite",
        "infinite totalities",
        "cardinality",
        "later theory",
        "handoff",
    )
    if any(phrase in lower for phrase in explicit_future_phrases):
        return "candidate_future_unit", "Story Critic explicitly frames the gap as later-unit/downstream work"
    if any(marker in lower for marker in future_spine_markers) and any(_similar(text, hint) >= 0.32 for hint in downstream_hints):
        return "candidate_future_unit", "Matches a rejected/withheld downstream question transition"
    return "supplementary", "Unresolved evidence can be filled without allocating a new research unit"


def build_gap_plan(unit_id: str, root: Path = ROOT) -> dict[str, Any]:
    unit_id = unit_id.upper()
    story_review_path = _one_review(root / "editorial/reviews", unit_id)
    research_review_path = _one_review(root / "research/reviews", unit_id)
    if story_review_path:
        review = _load(story_review_path) or {}
        raw_gaps = review.get("research_gaps") or []
        source_label = str(story_review_path.relative_to(root))
    elif research_review_path:
        review = _load(research_review_path) or {}
        raw_gaps = review.get("research_gaps") or []
        source_label = str(research_review_path.relative_to(root))
    else:
        raw_gaps, source_label = [], "<none>"

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
        proposal_id = str(gap.get("id") or f"gap-{unit_id.lower()}-proposal-{index:02d}")
        match = next((row for row in existing if _same_gap(proposal_id, question, row)), None)
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
            "supplementary": sum(row["kind"] == "supplementary" for row in proposals),
            "candidate_future_unit": sum(row["kind"] == "candidate_future_unit" for row in proposals),
            "already_registered": sum(bool(row["registered"]) for row in proposals),
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
        raise RuntimeError(f"{unit_id} already has multiple gap registry files; merge manually before automatic registration")
    path = existing_files[0] if existing_files else root / "research/gaps" / f"{unit_id}-followups.yaml"
    data = _load(path) if path.exists() else {"research_unit_id": unit_id, "research_gaps": []}
    if not isinstance(data, dict) or not isinstance(data.setdefault("research_gaps", []), list):
        raise RuntimeError(f"{path} is not a valid gap registry mapping")
    for proposal in missing:
        data["research_gaps"].append(_persistent_row(proposal))
    _save(path, data)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Propose persistent research gaps after Story Critic without allocating future R-numbers.")
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
        print(f"Summary: supplementary {summary['supplementary']} / candidate_future_unit {summary['candidate_future_unit']} / already registered {summary['already_registered']}")
    if args.apply:
        path = apply_gap_plan(plan)
        print("No registration changes: all proposed gaps are already persistent" if path is None else f"Registered gaps in {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
