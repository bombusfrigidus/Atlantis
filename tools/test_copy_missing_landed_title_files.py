"""Focused tests for copying files referenced by landed-title errors."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from copy_missing_landed_title_files import (
    copy_missing_files,
    extract_logged_paths,
    safe_relative_path,
)


class LandedTitleFileCopyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.game = self.root / "game"
        self.mod = self.root / "mod"
        self.game.mkdir()
        self.mod.mkdir()
        self.log = self.root / "error.log"

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_extracts_only_matching_unique_locations(self) -> None:
        text = "\n".join(
            (
                "Failed to fetch a valid landed title 'c_one' at location 'file: common/a.txt line: 12 (event)'",
                "Failed to fetch a valid landed title 'c_one' at location 'file: common/a.txt line: 12 (event)'",
                "Unknown modifier type at file: common/ignored.txt line: 5",
            )
        )
        self.assertEqual(extract_logged_paths(text), ["common/a.txt"])

    def test_safe_relative_path_rejects_absolute_and_parent_paths(self) -> None:
        self.assertIsNone(safe_relative_path("../outside.txt"))
        self.assertIsNone(safe_relative_path("C:\\outside.txt"))
        self.assertEqual(safe_relative_path("common\\events.txt"), Path("common/events.txt"))

    def test_copies_missing_file_and_never_overwrites_existing_file(self) -> None:
        source_new = self.game / "common" / "new.txt"
        source_existing = self.game / "common" / "edited.txt"
        source_new.parent.mkdir(parents=True)
        source_new.write_text("game copy\n", encoding="utf-8")
        source_existing.write_text("vanilla version\n", encoding="utf-8")
        destination_existing = self.mod / "common" / "edited.txt"
        destination_existing.parent.mkdir(parents=True)
        destination_existing.write_text("Atlantis edit\n", encoding="utf-8")
        self.log.write_text(
            "\n".join(
                (
                    "Failed to fetch a valid landed title 'c_new' at location 'file: common/new.txt line: 4 (test)'",
                    "Failed to fetch a valid landed title 'c_existing' at location 'file: common/edited.txt line: 8 (test)'",
                    "Failed to fetch a valid landed title 'c_new' at location 'file: common/new.txt line: 9 (test)'",
                )
            ),
            encoding="utf-8",
        )

        report = copy_missing_files(self.log, self.game, self.mod)

        self.assertEqual((self.mod / "common" / "new.txt").read_text(encoding="utf-8"), "game copy\n")
        self.assertEqual(destination_existing.read_text(encoding="utf-8"), "Atlantis edit\n")
        self.assertEqual(report.copied, (Path("common/new.txt"),))
        self.assertEqual(report.already_present, (Path("common/edited.txt"),))

    def test_missing_sources_and_unsafe_paths_are_reported(self) -> None:
        self.log.write_text(
            "\n".join(
                (
                    "Failed to fetch a valid landed title 'c_missing' at location 'file: common/missing.txt line: 4 (test)'",
                    "Failed to fetch a valid landed title 'c_unsafe' at location 'file: ../outside.txt line: 5 (test)'",
                )
            ),
            encoding="utf-8",
        )

        report = copy_missing_files(self.log, self.game, self.mod)

        self.assertEqual(report.missing_sources, (Path("common/missing.txt"),))
        self.assertEqual(report.rejected_paths, ("../outside.txt",))


if __name__ == "__main__":
    unittest.main()
