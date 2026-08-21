from pathlib import Path

import yaml

from scripts.common import ROOT
from scripts.propose_research_gaps import apply_gap_plan, build_gap_plan
from scripts.validate_story_evidence import validate_story_evidence


def test_r007_story_passes_evidence_gate():
    errors, warnings = validate_story_evidence(ROOT / "editorial/stories/r007-intrinsic-geometry.yaml")
    assert errors == []
    assert warnings == []


def test_r008_story_passes_with_explicit_strong_link_warnings():
    errors, warnings = validate_story_evidence(ROOT / "editorial/stories/r008-uniqueness.yaml")
    assert errors == []
    assert any("continues" in warning for warning in warnings)


def test_story_evidence_gate_rejects_missing_canonical_assertion(tmp_path: Path):
    story = [
        {
            "id": "story-test",
            "steps": [
                {
                    "id": "step-1",
                    "narrative": "A historical claim.",
                    "assertion_refs": ["assertion-does-not-exist"],
                    "perspective": "historical",
                }
            ],
            "links": [],
        }
    ]
    path = tmp_path / "story.yaml"
    path.write_text(yaml.safe_dump(story, sort_keys=False), encoding="utf-8")
    errors, _ = validate_story_evidence(path)
    assert any("missing canonical assertion" in error for error in errors)


def test_r008_gap_completion_replays_three_persistent_followups():
    plan = build_gap_plan("R008")
    assert len(plan["proposals"]) == 3
    assert plan["summary"]["supplementary"] == 2
    assert plan["summary"]["candidate_future_unit"] == 1
    assert plan["summary"]["already_registered"] == 3

    future = next(row for row in plan["proposals"] if row["kind"] == "candidate_future_unit")
    assert future["candidate_id"]
    assert not future["candidate_id"].upper().startswith("R0")
    assert "requires current roadmap review" in future["roadmap_eligibility"]
    assert "R009" in plan["roadmap_snapshot"]["allocated_unit_ids"]
    assert "R010" in plan["roadmap_snapshot"]["allocated_unit_ids"]


def test_gap_apply_writes_kinded_registry_without_r_number(tmp_path: Path):
    (tmp_path / "research/gaps").mkdir(parents=True)
    plan = {
        "research_unit_id": "R999",
        "proposals": [
            {
                "proposal_id": "gap-r999-supplement",
                "originating_unit": "R999",
                "kind": "supplementary",
                "question": "What evidence is missing?",
                "needed_evidence": "A primary locator.",
                "registered": False,
            },
            {
                "proposal_id": "gap-r999-next-spine",
                "originating_unit": "R999",
                "kind": "candidate_future_unit",
                "question": "What later bounded unit should test the handoff?",
                "needed_evidence": "Later primary sources.",
                "registered": False,
                "candidate_id": "r999-next-spine",
                "roadmap_eligibility": "unassigned; requires current roadmap review",
            },
        ],
    }
    path = apply_gap_plan(plan, tmp_path)
    assert path is not None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    rows = data["research_gaps"]
    assert {row["kind"] for row in rows} == {"supplementary", "candidate_future_unit"}
    future = next(row for row in rows if row["kind"] == "candidate_future_unit")
    assert future["candidate_id"] == "r999-next-spine"
    assert "roadmap" in future["roadmap_eligibility"]
