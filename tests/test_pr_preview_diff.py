from pathlib import Path
import subprocess

from scripts.pr_preview_diff import build_preview_diff


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()


def _run(repo: Path, *args: str) -> None:
    subprocess.check_call(["git", *args], cwd=repo)


def _write(repo: Path, name: str, text: str) -> None:
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_preview_diff_uses_current_merge_base_when_base_advances(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _run(repo, "init", "-b", "main")
    _run(repo, "config", "user.email", "test@example.com")
    _run(repo, "config", "user.name", "Test")

    _write(repo, "README.md", "root\n")
    _run(repo, "add", ".")
    _run(repo, "commit", "-m", "root")

    _run(repo, "checkout", "-b", "feature")
    _write(repo, "editorial/stories/r008.yaml", "story r008\n")
    _run(repo, "add", ".")
    _run(repo, "commit", "-m", "R008")
    feature_sha = _git(repo, "rev-parse", "HEAD")

    _run(repo, "checkout", "main")
    _write(repo, "editorial/stories/r007.yaml", "story r007\n")
    _run(repo, "add", ".")
    _run(repo, "commit", "-m", "R007 merged")

    result = build_preview_diff("main", feature_sha, cwd=repo)

    assert result["base_relation"] == "behind"
    assert result["behind"] == 1
    assert result["changed_files"] == ["editorial/stories/r008.yaml"]
