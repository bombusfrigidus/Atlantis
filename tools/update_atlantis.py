#!/usr/bin/env python3
"""Refresh Atlantis files that share paths with an installed CK3 game folder.

This is intentionally a file-level overwrite, not a Paradox-script-aware merge.
Back up the Atlantis directory and review the dry-run report before applying.
"""

from __future__ import annotations

import argparse
import filecmp
import os
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_MOD_ROOT = SCRIPT_DIR.parent
DEFAULT_GAME_ROOT = DEFAULT_MOD_ROOT.parent
DESCRIPTOR_NAMES = ("descriptor.mod", "Atlantis.mod")
SUPPORTED_VERSION_RE = re.compile(
    r'^(?P<prefix>[ \t]*supported_version[ \t]*=[ \t]*)["\'][^"\'\r\n]*["\'](?P<suffix>[ \t]*(?:#.*)?\r?)$',
    re.MULTILINE,
)


@dataclass(frozen=True)
class FileUpdate:
    relative_path: Path
    source: Path
    target: Path


def is_within(path: Path, root: Path) -> bool:
    """Return whether resolved path is equal to or below resolved root."""
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def discover_updates(game_root: Path, mod_root: Path) -> tuple[list[FileUpdate], list[Path], list[Path]]:
    """Find differing same-relative-path files; never add or delete mod files."""
    updates: list[FileUpdate] = []
    unchanged: list[Path] = []
    mod_only: list[Path] = []

    for target in sorted(mod_root.rglob("*")):
        if target.is_dir():
            continue
        if target.is_symlink():
            raise ValueError(f"Refusing to process symlink in mod tree: {target}")
        if not target.is_file():
            continue

        relative = target.relative_to(mod_root)
        source = game_root / relative
        if not is_within(source, game_root):
            raise ValueError(f"Source path escapes game root: {relative}")
        if not source.is_file():
            mod_only.append(relative)
            continue
        if source.is_symlink() or not is_within(source, game_root):
            raise ValueError(f"Refusing unsafe source path: {source}")

        if filecmp.cmp(source, target, shallow=False):
            unchanged.append(relative)
        else:
            updates.append(FileUpdate(relative, source, target))

    return updates, unchanged, mod_only


def updated_descriptor_text(path: Path, supported_version: str) -> str:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    replacement = f'"{supported_version}"'
    if SUPPORTED_VERSION_RE.search(text):
        return SUPPORTED_VERSION_RE.sub(
            lambda match: f"{match.group('prefix')}{replacement}{match.group('suffix')}",
            text,
        )

    ending = "" if not text or text.endswith(("\n", "\r")) else "\n"
    return f"{text}{ending}{replacement}\n"


def metadata_updates(mod_root: Path, supported_version: str) -> dict[Path, bytes]:
    result: dict[Path, bytes] = {}
    for name in DESCRIPTOR_NAMES:
        path = mod_root / name
        if path.is_file():
            text = updated_descriptor_text(path, supported_version)
            original = path.read_bytes()
            bom = b"\xef\xbb\xbf" if original.startswith(b"\xef\xbb\xbf") else b""
            data = bom + text.encode("utf-8")
            if original != data:
                result[Path(name)] = data
    return result


def default_backup_root(mod_root: Path) -> Path:
    return mod_root.parent / f"{mod_root.name}_update_backups"


def make_backup_dir(backup_root: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_dir = backup_root / timestamp
    backup_dir.mkdir(parents=True, exist_ok=False)
    return backup_dir


def write_atomically(target: Path, data: bytes) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, prefix=f".{target.name}.", delete=False) as temp:
            temporary_name = temp.name
            temp.write(data)
            temp.flush()
            os.fsync(temp.fileno())
        shutil.copystat(target, temporary_name, follow_symlinks=False)
        os.replace(temporary_name, target)
    finally:
        if temporary_name and os.path.exists(temporary_name):
            os.unlink(temporary_name)


def restore_backup(backup_dir: Path, mod_root: Path) -> int:
    backup_dir = backup_dir.resolve()
    mod_root = mod_root.resolve()
    if not backup_dir.is_dir():
        raise ValueError(f"Backup directory does not exist: {backup_dir}")

    restored = 0
    for saved_file in sorted(backup_dir.rglob("*")):
        if saved_file.is_dir():
            continue
        if saved_file.is_symlink() or not is_within(saved_file, backup_dir):
            raise ValueError(f"Refusing unsafe backup entry: {saved_file}")
        relative = saved_file.relative_to(backup_dir)
        destination = mod_root / relative
        if not is_within(destination, mod_root):
            raise ValueError(f"Restore path escapes mod root: {relative}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(saved_file, destination)
        restored += 1
    return restored


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Overwrite every differing Atlantis file whose relative path exists in the installed CK3 folder. "
            "Atlantis-only files are preserved. Dry-run is the default."
        )
    )
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME_ROOT, help="Installed CK3 game directory")
    parser.add_argument("--mod-root", type=Path, default=DEFAULT_MOD_ROOT, help="Atlantis mod directory")
    parser.add_argument(
        "--supported-version",
        default="1.20.*",
        help='Version string written to mod descriptors (default: "1.20.*")',
    )
    parser.add_argument("--backup-root", type=Path, help="Backup parent directory (default: sibling Atlantis_update_backups)")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--apply", action="store_true", help="Apply overwrites after backing up every affected file")
    action.add_argument("--restore-from", type=Path, help="Restore files from a timestamped backup directory")
    args = parser.parse_args(argv)

    if not re.fullmatch(r"[0-9]+\.[0-9]+(?:\.\*)?", args.supported_version):
        parser.error("--supported-version must look like 1.20.* or 1.20")
    return args


def run(args: argparse.Namespace) -> int:
    game_root = args.game_root.resolve()
    mod_root = args.mod_root.resolve()
    if not game_root.is_dir():
        raise ValueError(f"Game directory does not exist: {game_root}")
    if not mod_root.is_dir():
        raise ValueError(f"Mod directory does not exist: {mod_root}")
    if game_root == mod_root:
        raise ValueError("Game root and mod root must be different directories")

    if args.restore_from:
        count = restore_backup(args.restore_from, mod_root)
        print(f"Restored {count} file(s) from {args.restore_from}")
        return 0

    updates, unchanged, mod_only = discover_updates(game_root, mod_root)
    metadata = metadata_updates(mod_root, args.supported_version)
    metadata_paths = {Path(name) for name in DESCRIPTOR_NAMES if Path(name) in metadata}
    print(f"Game source : {game_root}")
    print(f"Atlantis    : {mod_root}")
    print(f"Differing shared files to overwrite: {len(updates)}")
    for item in updates:
        print(f"  OVERWRITE {item.relative_path}")
    print(f"Descriptor metadata updates: {len(metadata_paths)}")
    for path in sorted(metadata_paths):
        print(f"  VERSION   {path} -> {args.supported_version}")
    print(f"Unchanged shared files: {len(unchanged)}")
    print(f"Atlantis-only files preserved: {len(mod_only)}")

    if not args.apply:
        print("\nDry run only; no files were changed. Use --apply to back up and apply these updates.")
        return 0

    changes: list[tuple[Path, bytes]] = []
    for item in updates:
        changes.append((item.relative_path, item.source.read_bytes()))
    changes.extend((path, data) for path, data in metadata.items())
    if not changes:
        print("Nothing to update.")
        return 0

    backup_root = (args.backup_root or default_backup_root(mod_root)).resolve()
    if is_within(backup_root, mod_root):
        raise ValueError("Backup directory must be outside the Atlantis mod directory")
    backup_dir = make_backup_dir(backup_root)
    try:
        # Complete all backups before the first overwrite, so a backup error cannot
        # leave Atlantis partially refreshed.
        for relative, _ in changes:
            source_file = mod_root / relative
            if source_file.is_file():
                backup_file = backup_dir / relative
                backup_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, backup_file)

        for relative, data in changes:
            write_atomically(mod_root / relative, data)
    except Exception:
        print(f"Update failed. Any completed backups are available at: {backup_dir}", file=sys.stderr)
        raise

    print(f"Applied {len(changes)} update(s). Pre-update files backed up to: {backup_dir}")
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        return run(parse_args(argv))
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
