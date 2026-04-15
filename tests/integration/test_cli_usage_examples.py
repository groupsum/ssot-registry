from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, workspace_tempdir


class CliUsageExamplesTests(unittest.TestCase):
    def test_init_to_release_three_via_three_releases(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir(parents=True, exist_ok=True)

            init = run_cli("init", str(repo), "--repo-id", "repo:usage-example", "--repo-name", "usage-example", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            (repo / "tests").mkdir(exist_ok=True)
            (repo / "evidence").mkdir(exist_ok=True)
            (repo / "tests" / "test_r1.py").write_text("def test_r1():\n    assert True\n", encoding="utf-8")
            (repo / "tests" / "test_r2.py").write_text("def test_r2():\n    assert True\n", encoding="utf-8")
            (repo / "tests" / "test_r3.py").write_text("def test_r3():\n    assert True\n", encoding="utf-8")
            (repo / "evidence" / "r1.json").write_text("{\"ok\": true}\n", encoding="utf-8")
            (repo / "evidence" / "r2.json").write_text("{\"ok\": true}\n", encoding="utf-8")
            (repo / "evidence" / "r3.json").write_text("{\"ok\": true}\n", encoding="utf-8")

            self._run_ok(
                "feature",
                "create",
                str(repo),
                "--id",
                "feat:usage.alpha",
                "--title",
                "Alpha feature",
                "--implementation-status",
                "partial",
            )
            self._run_ok(
                "feature",
                "create",
                str(repo),
                "--id",
                "feat:usage.beta",
                "--title",
                "Beta feature",
                "--implementation-status",
                "partial",
            )
            self._run_ok(
                "feature",
                "create",
                str(repo),
                "--id",
                "feat:usage.gamma",
                "--title",
                "Gamma feature",
                "--implementation-status",
                "partial",
            )
            self._run_ok(
                "claim",
                "create",
                str(repo),
                "--id",
                "clm:usage.r1",
                "--title",
                "Release 1 claim",
                "--kind",
                "quality",
                "--tier",
                "T1",
                "--status",
                "asserted",
                "--feature-ids",
                "feat:usage.alpha",
            )
            self._run_ok(
                "claim",
                "create",
                str(repo),
                "--id",
                "clm:usage.r2",
                "--title",
                "Release 2 claim",
                "--kind",
                "quality",
                "--tier",
                "T1",
                "--status",
                "asserted",
                "--feature-ids",
                "feat:usage.beta",
            )
            self._run_ok(
                "claim",
                "create",
                str(repo),
                "--id",
                "clm:usage.r3",
                "--title",
                "Release 3 claim",
                "--kind",
                "quality",
                "--tier",
                "T1",
                "--status",
                "asserted",
                "--feature-ids",
                "feat:usage.gamma",
            )

            self._run_ok(
                "evidence",
                "create",
                str(repo),
                "--id",
                "evd:usage.r1",
                "--title",
                "R1 evidence",
                "--status",
                "passed",
                "--kind",
                "ci",
                "--tier",
                "T1",
                "--evidence-path",
                "evidence/r1.json",
                "--claim-ids",
                "clm:usage.r1",
            )
            self._run_ok(
                "evidence",
                "create",
                str(repo),
                "--id",
                "evd:usage.r2",
                "--title",
                "R2 evidence",
                "--status",
                "passed",
                "--kind",
                "ci",
                "--tier",
                "T1",
                "--evidence-path",
                "evidence/r2.json",
                "--claim-ids",
                "clm:usage.r2",
            )
            self._run_ok(
                "evidence",
                "create",
                str(repo),
                "--id",
                "evd:usage.r3",
                "--title",
                "R3 evidence",
                "--status",
                "passed",
                "--kind",
                "ci",
                "--tier",
                "T1",
                "--evidence-path",
                "evidence/r3.json",
                "--claim-ids",
                "clm:usage.r3",
            )

            self._run_ok(
                "test",
                "create",
                str(repo),
                "--id",
                "tst:usage.r1",
                "--title",
                "R1 test",
                "--status",
                "passing",
                "--kind",
                "unit",
                "--test-path",
                "tests/test_r1.py",
                "--feature-ids",
                "feat:usage.alpha",
                "--claim-ids",
                "clm:usage.r1",
                "--evidence-ids",
                "evd:usage.r1",
            )
            self._run_ok(
                "test",
                "create",
                str(repo),
                "--id",
                "tst:usage.r2",
                "--title",
                "R2 test",
                "--status",
                "passing",
                "--kind",
                "integration",
                "--test-path",
                "tests/test_r2.py",
                "--feature-ids",
                "feat:usage.beta",
                "--claim-ids",
                "clm:usage.r2",
                "--evidence-ids",
                "evd:usage.r2",
            )
            self._run_ok(
                "test",
                "create",
                str(repo),
                "--id",
                "tst:usage.r3",
                "--title",
                "R3 test",
                "--status",
                "passing",
                "--kind",
                "e2e",
                "--test-path",
                "tests/test_r3.py",
                "--feature-ids",
                "feat:usage.gamma",
                "--claim-ids",
                "clm:usage.r3",
                "--evidence-ids",
                "evd:usage.r3",
            )
            self._run_ok("claim", "link", str(repo), "--id", "clm:usage.r1", "--test-ids", "tst:usage.r1", "--evidence-ids", "evd:usage.r1")
            self._run_ok("claim", "link", str(repo), "--id", "clm:usage.r2", "--test-ids", "tst:usage.r2", "--evidence-ids", "evd:usage.r2")
            self._run_ok("claim", "link", str(repo), "--id", "clm:usage.r3", "--test-ids", "tst:usage.r3", "--evidence-ids", "evd:usage.r3")
            self._run_ok("evidence", "link", str(repo), "--id", "evd:usage.r1", "--test-ids", "tst:usage.r1")
            self._run_ok("evidence", "link", str(repo), "--id", "evd:usage.r2", "--test-ids", "tst:usage.r2")
            self._run_ok("evidence", "link", str(repo), "--id", "evd:usage.r3", "--test-ids", "tst:usage.r3")
            self._run_ok("feature", "link", str(repo), "--id", "feat:usage.alpha", "--claim-ids", "clm:usage.r1", "--test-ids", "tst:usage.r1")
            self._run_ok("feature", "link", str(repo), "--id", "feat:usage.beta", "--claim-ids", "clm:usage.r2", "--test-ids", "tst:usage.r2")
            self._run_ok("feature", "link", str(repo), "--id", "feat:usage.gamma", "--claim-ids", "clm:usage.r3", "--test-ids", "tst:usage.r3")
            self._run_ok("feature", "plan", str(repo), "--ids", "feat:usage.alpha", "--horizon", "current", "--claim-tier", "T1")
            self._run_ok("feature", "plan", str(repo), "--ids", "feat:usage.beta", "--horizon", "current", "--claim-tier", "T1")
            self._run_ok("feature", "plan", str(repo), "--ids", "feat:usage.gamma", "--horizon", "explicit", "--slot", "r3", "--claim-tier", "T1")
            self._run_ok("feature", "update", str(repo), "--id", "feat:usage.alpha", "--implementation-status", "implemented")
            self._run_ok("feature", "update", str(repo), "--id", "feat:usage.beta", "--implementation-status", "implemented")
            self._run_ok("feature", "update", str(repo), "--id", "feat:usage.gamma", "--implementation-status", "implemented")

            self._run_ok(
                "boundary",
                "create",
                str(repo),
                "--id",
                "bnd:rel1",
                "--title",
                "Release 1 boundary",
                "--feature-ids",
                "feat:usage.alpha",
            )
            self._run_ok("release", "add-claim", str(repo), "--id", "rel:1.0.0", "--claim-ids", "clm:usage.r1")
            self._run_ok("release", "add-evidence", str(repo), "--id", "rel:1.0.0", "--evidence-ids", "evd:usage.r1")
            self._run_ok("boundary", "freeze", str(repo), "--boundary-id", "bnd:rel1")
            self._run_ok("release", "update", str(repo), "--id", "rel:1.0.0", "--boundary-id", "bnd:rel1")
            self._run_ok("release", "certify", str(repo), "--release-id", "rel:1.0.0")
            self._run_ok("release", "promote", str(repo), "--release-id", "rel:1.0.0")
            self._run_ok("release", "publish", str(repo), "--release-id", "rel:1.0.0")

            self._run_ok(
                "boundary",
                "create",
                str(repo),
                "--id",
                "bnd:rel2",
                "--title",
                "Release 2 boundary",
                "--feature-ids",
                "feat:usage.alpha",
                "feat:usage.beta",
            )
            self._run_ok("boundary", "freeze", str(repo), "--boundary-id", "bnd:rel2")

            self._run_ok(
                "release",
                "create",
                str(repo),
                "--id",
                "rel:2.0.0",
                "--version",
                "2.0.0",
                "--boundary-id",
                "bnd:rel2",
                "--claim-ids",
                "clm:usage.r1",
                "clm:usage.r2",
                "--evidence-ids",
                "evd:usage.r1",
                "evd:usage.r2",
            )

            premature_publish = run_cli("release", "publish", str(repo), "--release-id", "rel:2.0.0")
            self.assertNotEqual(premature_publish.returncode, 0, premature_publish.stdout + premature_publish.stderr)
            self.assertIn("must be promoted before publication", premature_publish.stdout)

            self._run_ok("release", "certify", str(repo), "--release-id", "rel:2.0.0")
            self._run_ok("release", "promote", str(repo), "--release-id", "rel:2.0.0")
            self._run_ok("release", "publish", str(repo), "--release-id", "rel:2.0.0")
            self._run_ok(
                "boundary",
                "create",
                str(repo),
                "--id",
                "bnd:rel3",
                "--title",
                "Release 3 boundary",
                "--feature-ids",
                "feat:usage.alpha",
                "feat:usage.beta",
                "feat:usage.gamma",
            )
            self._run_ok("boundary", "freeze", str(repo), "--boundary-id", "bnd:rel3")

            self._run_ok(
                "release",
                "create",
                str(repo),
                "--id",
                "rel:3.0.0",
                "--version",
                "3.0.0",
                "--boundary-id",
                "bnd:rel3",
                "--claim-ids",
                "clm:usage.r1",
                "clm:usage.r2",
                "clm:usage.r3",
                "--evidence-ids",
                "evd:usage.r1",
                "evd:usage.r2",
                "evd:usage.r3",
            )

            premature_promote = run_cli("release", "promote", str(repo), "--release-id", "rel:3.0.0")
            self.assertNotEqual(premature_promote.returncode, 0, premature_promote.stdout + premature_promote.stderr)
            self.assertIn("must be certified before promotion", premature_promote.stdout)

            self._run_ok("release", "certify", str(repo), "--release-id", "rel:3.0.0")
            self._run_ok("release", "promote", str(repo), "--release-id", "rel:3.0.0")
            self._run_ok("release", "publish", str(repo), "--release-id", "rel:3.0.0")

            recertify = run_cli("release", "certify", str(repo), "--release-id", "rel:3.0.0")
            self.assertNotEqual(recertify.returncode, 0, recertify.stdout + recertify.stderr)
            self.assertIn("must be draft or candidate before certification", recertify.stdout)

            registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))
            self.assertEqual(self._release_status(registry, "rel:1.0.0"), "published")
            self.assertEqual(self._release_status(registry, "rel:2.0.0"), "published")
            self.assertEqual(self._release_status(registry, "rel:3.0.0"), "published")

    def _run_ok(self, *args: str) -> dict[str, object]:
        result = run_cli(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["passed"], payload)
        return payload

    def _release_status(self, registry: dict[str, object], release_id: str) -> str:
        for row in registry["releases"]:
            if row["id"] == release_id:
                return row["status"]
        raise AssertionError(f"missing release id: {release_id}")


if __name__ == "__main__":
    unittest.main()
