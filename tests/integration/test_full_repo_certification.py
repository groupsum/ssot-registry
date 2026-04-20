from __future__ import annotations

import shutil
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORE_SRC_ROOT = PROJECT_ROOT / "pkgs" / "ssot-core" / "src"
if str(CORE_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(CORE_SRC_ROOT))

from ssot_registry.api import certify_release, load_registry, promote_release, publish_release, validate_registry
from tests.helpers import workspace_tempdir


class FullRepoCertificationTests(unittest.TestCase):
    def test_full_repo_release_can_certify_promote_and_publish_from_temp_copy(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            shutil.copytree(PROJECT_ROOT / ".ssot", repo / ".ssot")
            shutil.copytree(PROJECT_ROOT / "tests", repo / "tests")

            validation = validate_registry(repo)
            self.assertTrue(validation["passed"], validation)

            certify = certify_release(repo, release_id="rel:full-cert", write_report=True)
            self.assertTrue(certify["passed"])
            self.assertTrue((repo / ".ssot" / "reports" / "certification.report.json").exists())

            promote = promote_release(repo, release_id="rel:full-cert")
            self.assertTrue(promote["passed"])
            self.assertTrue((repo / ".ssot" / "reports" / "promotion.report.json").exists())

            publish = publish_release(repo, release_id="rel:full-cert")
            self.assertTrue(publish["passed"])
            self.assertTrue((repo / ".ssot" / "reports" / "publication.report.json").exists())

            _registry_path, _repo_root, registry = load_registry(repo)
            release = next(row for row in registry["releases"] if row["id"] == "rel:full-cert")
            self.assertEqual(release["status"], "published")
