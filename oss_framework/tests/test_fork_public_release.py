import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "fork_public_release.py"


def git(*args: str, cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def test_fork_public_release_creates_fresh_repository(tmp_path) -> None:
    source_repo = tmp_path / "source-repo"
    export_repo = tmp_path / "export-repo"
    source_repo.mkdir()

    git("init", "-b", "main", cwd=source_repo)
    git("config", "user.name", "Test User", cwd=source_repo)
    git("config", "user.email", "test@example.com", cwd=source_repo)

    (source_repo / "README.md").write_text("# Example public release\n")
    (source_repo / "tracked.txt").write_text("tracked content\n")
    (source_repo / "private.txt").write_text("untracked and should not be exported\n")

    git("add", "README.md", "tracked.txt", cwd=source_repo)
    git("commit", "-m", "Seed branch", cwd=source_repo)
    git("checkout", "-b", "copilot/public-release", cwd=source_repo)

    subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--source-repo",
            str(source_repo),
            "--source-branch",
            "copilot/public-release",
            "--target-dir",
            str(export_repo),
            "--remote-url",
            "https://github.com/example/local-data-stack.git",
            "--skip-validation",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert (export_repo / ".git").exists()
    assert (export_repo / "README.md").read_text() == "# Example public release\n"
    assert (export_repo / "tracked.txt").read_text() == "tracked content\n"
    assert not (export_repo / "private.txt").exists()
    assert git("rev-parse", "--abbrev-ref", "HEAD", cwd=export_repo) == "main"
    assert git("rev-list", "--count", "HEAD", cwd=export_repo) == "1"
    assert (
        git("remote", "get-url", "origin", cwd=export_repo)
        == "https://github.com/example/local-data-stack.git"
    )
