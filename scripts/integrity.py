from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_bytes(data: Any) -> bytes:
    """Serialize YAML-loaded data deterministically for content fingerprints."""
    return json.dumps(
        data,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


def fingerprint(data: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(data)).hexdigest()


def validate_finding_ids(review: dict[str, Any]) -> None:
    findings = review.get("findings", [])
    if not isinstance(findings, list):
        raise ValueError("Review 'findings' must be a list.")

    ids: list[str] = []
    for index, row in enumerate(findings, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"Review finding #{index} is not a mapping.")
        finding_id = str(row.get("id", "")).strip()
        if not finding_id:
            raise ValueError(
                f"Review finding #{index} is missing a stable 'id'."
            )
        ids.append(finding_id)

    duplicates = sorted({x for x in ids if ids.count(x) > 1})
    if duplicates:
        raise ValueError(f"Duplicate review finding IDs: {duplicates}")


def artifact_integrity(packet: dict[str, Any], review: dict[str, Any]) -> dict[str, str]:
    return {
        "packet_sha256": fingerprint(packet),
        "review_sha256": fingerprint(review),
    }


def require_integrity_match(
    stored: dict[str, Any] | None,
    packet: dict[str, Any],
    review: dict[str, Any],
    *,
    artifact_name: str,
) -> None:
    if not isinstance(stored, dict):
        raise RuntimeError(
            f"{artifact_name} has no integrity block; recreate it from the current packet/review."
        )

    current = artifact_integrity(packet, review)
    mismatches = [
        key for key, value in current.items()
        if str(stored.get(key, "")) != value
    ]
    if mismatches:
        details = ", ".join(mismatches)
        raise RuntimeError(
            f"{artifact_name} is stale ({details}); review the current artifacts again before promotion."
        )
