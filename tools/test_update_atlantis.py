"""Focused filesystem tests for update_atlantis.py."""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import update_atlantis


class UpdaterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.game = self.root / "game"
        self.mod = self.game / "Atlantis"
        (self.game / "common" / "sample").mkdir(parents=True)
        (self.mod / "common" / "sample").mkdir(parents=True)

        (self.game / "common" / "sample" / "shared.txt").write_text("vanilla 1.20\n", encoding="utf-8")
        (self.mod / "common" / "sample" / "shared.txt").write_text("Atlantis edits\n", encoding="utf-8")
        (self.game / "common" / "sample" / "game_only.txt").write_text("not copied\n", encoding="utf-8")
        (self.mod / "atlantis_only.txt").write_text("preserve me\n", encoding="utf-8")
        (self.mod / "descriptor.mod").write_text('name="Atlantis"\nsupported_version="1.16.*"\n', encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def args(self, *extra: str):
        return update_atlantis.parse_args(
            ["--game-root", str(self.game), "--mod-root", str(self.mod), *extra]
        )

    def test_dry_run_does_not_modify_files(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(update_atlantis.run(self.args()), 0)

        self.assertEqual((self.mod / "common/sample/shared.txt").read_text(encoding="utf-8"), "Atlantis edits\n")
        self.assertIn("OVERWRITE common\\sample\\shared.txt", output.getvalue())
        self.assertIn("Atlantis-only files preserved", output.getvalue())

    def test_apply_backs_up_overwrites_shared_and_updates_metadata(self) -> None:
        backup_root = self.root / "backups"
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(update_atlantis.run(self.args("--apply", "--backup-root", str(backup_root))), 0)

        self.assertEqual((self.mod / "common/sample/shared.txt").read_text(encoding="utf-8"), "vanilla 1.20\n")
        self.assertEqual((self.mod / "atlantis_only.txt").read_text(encoding="utf-8"), "preserve me\n")
        self.assertIn('supported_version="1.20.*"', (self.mod / "descriptor.mod").read_text(encoding="utf-8"))

        backup_dirs = list(backup_root.iterdir())
        self.assertEqual(len(backup_dirs), 1)
        backup_dir = backup_dirs[0]
        self.assertEqual(
            (backup_dir / "common/sample/shared.txt").read_text(encoding="utf-8"),
            "Atlantis edits\n",
        )
        self.assertIn(
            'supported_version="1.16.*"',
            (backup_dir / "descriptor.mod").read_text(encoding="utf-8"),
        )

        restored = update_atlantis.restore_backup(backup_dir, self.mod)
        self.assertEqual(restored, 2)
        self.assertEqual((self.mod / "common/sample/shared.txt").read_text(encoding="utf-8"), "Atlantis edits\n")
        self.assertIn('supported_version="1.16.*"', (self.mod / "descriptor.mod").read_text(encoding="utf-8"))

    def test_symlinked_mod_file_is_rejected(self) -> None:
        link = self.mod / "unsafe.txt"
        try:
            link.symlink_to(self.mod / "atlantis_only.txt")
        except OSError as error:
            self.skipTest(f"Creating symlinks is not permitted in this Windows environment: {error}")
        with self.assertRaisesRegex(ValueError, "symlink"):
            update_atlantis.discover_updates(self.game, self.mod)


if __name__ == "__main__":
    unittest.main()
