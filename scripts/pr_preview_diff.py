from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import yaml


def _git(*args: str, cwd: Path | None = None) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def build_preview_diff(base_ref: str, head_ref: str = "HEAD", cwd: Path | None = None) -> dict:
    merge_base = _git("merge-base", head_ref, base_ref, cwd=cwd)
    changed = _git("diff", "--name-only", merge_base, head_ref, cwd=cwd)
    counts = _git("rev-list", "--left-right", "--count", f"{head_ref}...{base_ref}", cwd=cwd)
    ahead_s, behind_s = counts.split()
    ahead = int(ahead_s)
    behind = int(behind_s)
    return {
        "base_ref": base_ref,
        "head_ref": head_ref,
        "merge_base": merge_base,
        "ahead": ahead,
        "behind": behind,
        "base_relation": "current" if behind == 0 else "behind",
        "changed_files": changed.splitlines() if changed else [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Describe PR changes against the current merge base of the target branch."
    )
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--output")
    args = parser.parse_args()

    result = build_preview_diff(args.base, args.head)
    rendered = yaml.safe_dump(result, sort_keys=False)
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
