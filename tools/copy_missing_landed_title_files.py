#!/usr/bin/env python3
"""Copy missing game files referenced by landed-title errors into Atlantis.

Run from any working directory with:
    python tools/copy_missing_landed_title_files.py

Only files mentioned by "Failed to fetch a valid landed title" log entries
are considered. Existing mod files are never overwritten.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_MOD_ROOT = SCRIPT_DIR.parent
# Change this to the full folder path where Crusader Kings III is installed.
GAME_FOLDER = Path(r"F:\Steam\steamapps\common\Crusader Kings III\game")
DEFAULT_GAME_ROOT = GAME_FOLDER
# Change this to the full path of your CK3 error.log.
ERROR_LOG = Path(r"C:\Users\Thor\Documents\Paradox Interactive\Crusader Kings III\logs\error.log")
DEFAULT_LOG = ERROR_LOG
TITLE_ERROR_RE = re.compile(
    r"Failed to fetch a valid landed title\b.*?at location\s+['\"]file:\s*"
    r"(?P<path>.+?)\s+line:\s*\d+\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CopyReport:
    copied: tuple[Path, ...]
    already_present: tuple[Path, ...]
    missing_sources: tuple[Path, ...]
    rejected_paths: tuple[str, ...]


def extract_logged_paths(log_text: str) -> list[str]:
    """Return unique file paths from matching landed-title log entries."""
    paths: list[str] = []
    seen: set[str] = set()
    for match in TITLE_ERROR_RE.finditer(log_text):
        logged_path = match.group("path").strip()
        if logged_path not in seen:
            seen.add(logged_path)
            paths.append(logged_path)
    return paths


def safe_relative_path(logged_path: str) -> Path | None:
    """Convert a logged game-relative path to a safe local relative path."""
    normalized = logged_path.replace("\\", "/")
    posix_path = PurePosixPath(normalized)
    windows_path = PureWindowsPath(logged_path)
    if (
        not normalized
        or posix_path.is_absolute()
        or windows_path.is_absolute()
        or windows_path.drive
        or any(part in ("", ".", "..") for part in posix_path.parts)
    ):
        return None
    return Path(*posix_path.parts)


def is_within(path: Path, root: Path) -> bool:
    """Whether a resolved path is equal to or beneath the resolved root."""
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def copy_missing_files(log_path: Path, game_root: Path, mod_root: Path) -> CopyReport:
    """Copy referenced files absent from the mod, preserving their relative paths."""
    game_root = game_root.resolve()
    mod_root = mod_root.resolve()
    log_text = log_path.read_text(encoding="utf-8-sig", errors="replace")

    copied: list[Path] = []
    already_present: list[Path] = []
    missing_sources: list[Path] = []
    rejected_paths: list[str] = []

    for logged_path in extract_logged_paths(log_text):
        relative = safe_relative_path(logged_path)
        if relative is None:
            rejected_paths.append(logged_path)
            continue

        source = game_root / relative
        destination = mod_root / relative
        if not is_within(source, game_root) or not is_within(destination, mod_root):
            rejected_paths.append(logged_path)
            continue
        if destination.exists() or destination.is_symlink():
            already_present.append(relative)
            continue
        if source.is_symlink() or not source.is_file() or not is_within(source, game_root):
            missing_sources.append(relative)
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        # Recheck after creating parents; never replace an existing file.
        if destination.exists() or destination.is_symlink():
            already_present.append(relative)
            continue
        shutil.copy2(source, destination)
        copied.append(relative)

    return CopyReport(
        copied=tuple(copied),
        already_present=tuple(already_present),
        missing_sources=tuple(missing_sources),
        rejected_paths=tuple(rejected_paths),
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Copy missing game files referenced by landed-title errors from the CK3 "
            "error log into Atlantis. Existing mod files are left untouched."
        )
    )
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG, help="CK3 error log path")
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME_ROOT, help="CK3 installation directory")
    parser.add_argument("--mod-root", type=Path, default=DEFAULT_MOD_ROOT, help="Atlantis mod directory")
    return parser.parse_args(argv)


def run(args: argparse.Namespace) -> int:
    game_root = args.game_root.resolve()
    mod_root = args.mod_root.resolve()
    if not game_root.is_dir():
        raise ValueError(f"CK3 game directory does not exist: {game_root}")
    if not mod_root.is_dir():
        raise ValueError(f"Atlantis mod directory does not exist: {mod_root}")
    if game_root == mod_root:
        raise ValueError("Game root and mod root must be different directories")
    if not args.log.is_file():
        raise ValueError(f"Error log does not exist: {args.log}")

    report = copy_missing_files(args.log, game_root, mod_root)
    print(f"Copied into Atlantis: {len(report.copied)}")
    for path in report.copied:
        print(f"  COPIED  {path}")
    print(f"Already present (left unchanged): {len(report.already_present)}")
    for path in report.already_present:
        print(f"  SKIPPED {path}")
    print(f"Missing source files: {len(report.missing_sources)}")
    for path in report.missing_sources:
        print(f"  MISSING {path}")
    print(f"Unsafe paths rejected: {len(report.rejected_paths)}")
    for path in report.rejected_paths:
        print(f"  REJECTED {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        return run(parse_args(argv))
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
