from pathlib import Path

import yaml

from scripts.common import ROOT
from scripts.story_architecture_review import (
    build_architecture_context,
    validate_architecture_review,
)


def _story(context: dict, story_id: str) -> dict:
    return next(row for row in context["stories"] if row["story_id"] == story_id)


def _overlap(context: dict, left: str, right: str) -> dict:
    pair = sorted([left, right])
    return next(row for row in context["overlaps"] if row["stories"] == pair)


def test_function_story_context_exposes_bounded_entry_and_fourier_overlap():
    context = build_architecture_context(["story-function"])
    story = _story(context, "story-function")
    assert story["entry"]["from"] == 1807
    assert story["entry"]["ref"] == "concept-fourier-series"

    overlap = _overlap(context, "story-function", "story-fourier-heat-representation")
    assert "q-what-is-function" in overlap["shared_question_phases"]
    assert "concept-fourier-series" in overlap["shared_step_refs"]


def test_fourier_heat_context_keeps_heat_question_in_story_path():
    context = build_architecture_context(["story-fourier-heat-representation"])
    story = _story(context, "story-fourier-heat-representation")
    assert story["question_phases"][0] == "q-heat-propagation"
    assert any(
        step["question_id"] == "q-heat-propagation"
        for step in story["question_steps"]
    )
    assert "q-heat-prescribed-data" in story["question_phases"]
    assert "q-trig-representation-scope" in story["question_phases"]


def test_fourier_heat_context_exposes_candidate_neighbor_network_edge():
    context = build_architecture_context(["story-fourier-heat-representation"])
    story = _story(context, "story-fourier-heat-representation")
    edge = next(
        row
        for row in story["neighbor_question_edges"]
        if row["assertion_id"] == "assertion-heat-to-convergence"
    )
    assert edge["subject"] == "q-heat-propagation"
    assert edge["object"] == "q-series-convergence"
    assert edge["predicate"] == "spawned"
    assert edge["perspective"] == "later_interpretation"
    assert edge["status"] == "candidate"


def test_r002_r005_context_exposes_existing_uniformity_intersection():
    context = build_architecture_context(
        ["story-cauchy-rigor-continuity", "story-quantified-control"]
    )
    overlap = _overlap(context, "story-cauchy-rigor-continuity", "story-quantified-control")
    assert "q-uniform-convergence-emergence" in overlap["shared_question_phases"]


def test_r008_context_preserves_question_spine_order():
    context = build_architecture_context(["story-r008-uniqueness"])
    story = _story(context, "story-r008-uniqueness")
    assert story["question_phases"] == [
        "q-fourier-series-convergence",
        "q-trig-series-uniqueness",
        "q-exceptional-set-uniqueness",
        "q-derived-set-structure",
    ]


def test_r008_context_exposes_network_edge_strengths():
    context = build_architecture_context(["story-r008-uniqueness"])
    story = _story(context, "story-r008-uniqueness")
    by_id = {row["assertion_id"]: row for row in story["question_phase_edges"]}
    assert {
        "assertion-r008-convergence-to-uniqueness-question",
        "assertion-r008-uniqueness-to-exceptional-question",
        "assertion-r008-exceptional-to-derived-question",
    } <= set(by_id)
    assert by_id["assertion-r008-convergence-to-uniqueness-question"]["perspective"] == "later_interpretation"
    assert by_id["assertion-r008-convergence-to-uniqueness-question"]["status"] == "historically_reviewed"
    assert by_id["assertion-r008-uniqueness-to-exceptional-question"]["perspective"] == "historical"
    assert by_id["assertion-r008-exceptional-to-derived-question"]["perspective"] == "historical"


def test_persistent_story_architecture_review_is_valid():
    errors = validate_architecture_review(
        ROOT / "editorial/reviews/story-architecture-review-2026-08.yaml"
    )
    assert errors == []


def test_entry_context_gap_cannot_directly_allocate_future_unit(tmp_path: Path):
    review = {
        "review": {
            "type": "story_architecture",
            "stories": ["story-function"],
        },
        "findings": [
            {
                "id": "sar-test",
                "classification": "REVISE",
                "dimension": "entry",
                "stories": ["story-function"],
                "reason": "The entry needs light context.",
                "gap": {
                    "kind": "entry_context",
                    "research_burden": "light",
                    "resolution_mode": "candidate_future_unit",
                },
            }
        ],
    }
    path = tmp_path / "review.yaml"
    path.write_text(yaml.safe_dump(review, sort_keys=False), encoding="utf-8")
    errors = validate_architecture_review(path)
    assert any("must not auto-escalate" in error for error in errors)
