import subprocess
import sys

import yaml

from scripts.common import ROOT


def _one(directory, pattern):
    matches = sorted(directory.glob(pattern))
    assert len(matches) == 1
    return matches[0]


def test_status_reports_completed_r008_without_mutation():
    tracked = [
        _one(ROOT / "research/packets", "R008-*.yaml"),
        _one(ROOT / "research/reviews", "R008-*.yaml"),
        _one(ROOT / "research/resolutions", "R008-*-resolution.yaml"),
    ]
    before = {path: path.read_bytes() for path in tracked}
    result = subprocess.run(
        [sys.executable, "-m", "scripts.research_unit_status", "R008"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Packet      ✓ valid" in result.stdout
    assert "Integrity   ✓ fingerprints current" in result.stdout
    assert "READY: validation / mobile review" in result.stdout
    assert before == {path: path.read_bytes() for path in tracked}


def test_research_unit_ops_is_permanent_dispatch_workflow():
    workflow = yaml.safe_load((ROOT / ".github/workflows/research-unit-ops.yml").read_text(encoding="utf-8"))
    on_block = workflow.get("on", workflow.get(True))
    dispatch = on_block["workflow_dispatch"]
    assert set(dispatch["inputs"]["operation"]["options"]) >= {
        "status",
        "check",
        "bind",
        "promote-dry-run",
        "promote-apply",
    }
