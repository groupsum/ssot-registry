from __future__ import annotations

import unittest
from pathlib import Path

from ssot_registry.api import create_document, create_document_reservation, initialize_repo
from ssot_registry.util.errors import ValidationError
from tests.helpers import workspace_tempdir


class DocumentReservationTests(unittest.TestCase):
    def test_repo_local_document_cannot_use_ssot_range(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            initialize_repo(repo, repo_id="repo:reservation-test", repo_name="reservation-test", version="1.0.0")
            body = repo / "adr-body.md"
            body.write_text("Reservation body.\n", encoding="utf-8")

            with self.assertRaises(ValidationError):
                create_document(repo, "adr", title="Bad ADR", slug="bad-adr", body_file=body, number=1)

    def test_overlapping_reservation_is_rejected(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            initialize_repo(repo, repo_id="repo:reservation-overlap", repo_name="reservation-overlap", version="1.0.0")

            with self.assertRaises(ValidationError):
                create_document_reservation(repo, "spec", name="overlap", start=900, end=1200)


if __name__ == "__main__":
    unittest.main()
