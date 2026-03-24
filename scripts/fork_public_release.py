#!/usr/bin/env python3
"""
Create a clean standalone repository from a public-release branch.

The export intentionally drops git history by archiving the tracked files from the
source branch and re-initializing a fresh repository in the target directory.
That keeps the public project focused on the sanitized snapshot rather than the
private repository history that produced it.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VALIDATION_COMMAND = [
    sys.executable,
    "-m",
    "pytest",
    "oss_framework/tests/test_public_release_sanitization.py",
    "-q",
    "--no-cov",
]


def run_command(
    command: list[str], *, cwd: Path, error_message: str
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        stderr = error.stderr.strip()
        stdout = error.stdout.strip()
        details = stderr or stdout or str(error)
        raise RuntimeError(f"{error_message}: {details}") from error


def ensure_git_repository(source_repo: Path) -> Path:
    if not (source_repo / ".git").exists():
        raise RuntimeError(f"{source_repo} is not a git repository")
    return source_repo


def ensure_branch_exists(source_repo: Path, source_branch: str) -> None:
    run_command(
        ["git", "rev-parse", "--verify", f"{source_branch}^{{commit}}"],
        cwd=source_repo,
        error_message=f"Branch '{source_branch}' was not found",
    )


def safe_extract_archive(archive_path: Path, target_dir: Path) -> None:
    with tarfile.open(archive_path) as archive:
        base_path = target_dir.resolve()
        for member in archive.getmembers():
            member_path = (base_path / member.name).resolve()
            if member_path != base_path and base_path not in member_path.parents:
                raise RuntimeError(
                    f"Refusing to extract archive member outside target directory: {member.name}"
                )
        archive.extractall(target_dir, filter="data")


def export_branch_snapshot(source_repo: Path, source_branch: str, target_dir: Path) -> None:
    if target_dir.exists() and any(target_dir.iterdir()):
        raise RuntimeError(f"Target directory must not already contain files: {target_dir}")

    target_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix=".tar", delete=False) as temporary_archive:
        archive_path = Path(temporary_archive.name)

    try:
        run_command(
            ["git", "archive", "--format=tar", f"--output={archive_path}", source_branch],
            cwd=source_repo,
            error_message=f"Failed to archive branch '{source_branch}'",
        )
        safe_extract_archive(archive_path, target_dir)
    finally:
        archive_path.unlink(missing_ok=True)


def initialize_repository(
    target_dir: Path, target_branch: str, source_branch: str, remote_url: str | None
) -> None:
    try:
        run_command(
            ["git", "init", "-b", target_branch],
            cwd=target_dir,
            error_message="Failed to initialize the new repository",
        )
    except RuntimeError:
        run_command(
            ["git", "init"],
            cwd=target_dir,
            error_message="Failed to initialize the new repository",
        )
        run_command(
            ["git", "checkout", "-b", target_branch],
            cwd=target_dir,
            error_message=f"Failed to create target branch '{target_branch}'",
        )

    run_command(
        ["git", "add", "."],
        cwd=target_dir,
        error_message="Failed to stage exported files",
    )
    run_command(
        [
            "git",
            "-c",
            "user.name=Public Release Export",
            "-c",
            "user.email=public-release-export@local.invalid",
            "commit",
            "-m",
            f"Initial import from {source_branch}",
        ],
        cwd=target_dir,
        error_message="Failed to create the initial commit in the new repository",
    )

    if remote_url:
        run_command(
            ["git", "remote", "add", "origin", remote_url],
            cwd=target_dir,
            error_message=f"Failed to configure origin remote '{remote_url}'",
        )


def run_release_validation(source_repo: Path) -> None:
    run_command(
        DEFAULT_VALIDATION_COMMAND,
        cwd=source_repo,
        error_message="Public release validation failed",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a sanitized branch into a fresh standalone git repository."
    )
    parser.add_argument(
        "--source-repo",
        default=str(REPO_ROOT),
        help="Path to the existing repository (defaults to the current repo).",
    )
    parser.add_argument(
        "--source-branch",
        default="copilot/public-release",
        help="Branch to export into the new project.",
    )
    parser.add_argument(
        "--target-dir",
        required=True,
        help="Directory where the new repository should be created.",
    )
    parser.add_argument(
        "--target-branch",
        default="main",
        help="Default branch name for the new repository.",
    )
    parser.add_argument(
        "--remote-url",
        help="Optional origin URL to configure in the newly created repository.",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip the public release sanitization pytest command before exporting.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_repo = ensure_git_repository(Path(args.source_repo).resolve())
    target_dir = Path(args.target_dir).resolve()

    ensure_branch_exists(source_repo, args.source_branch)

    if not args.skip_validation:
        print("Running public release validation...")
        run_release_validation(source_repo)

    print(f"Exporting {args.source_branch} from {source_repo} into {target_dir}...")
    export_branch_snapshot(source_repo, args.source_branch, target_dir)
    initialize_repository(target_dir, args.target_branch, args.source_branch, args.remote_url)

    print(f"Created a fresh repository at {target_dir}")
    print(f"Default branch: {args.target_branch}")
    if args.remote_url:
        print(f"Origin remote: {args.remote_url}")
        print(f"Next step: cd {target_dir} && git push -u origin {args.target_branch}")
    else:
        print("Next step: create a new remote repository and push this directory to it.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
