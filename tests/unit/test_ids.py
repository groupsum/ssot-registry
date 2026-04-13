from __future__ import annotations

import unittest

from ssot_registry.model.ids import filesystem_safe_id, is_normalized_id


class IdNormalizationTests(unittest.TestCase):
    def test_accepts_normalized_ids(self) -> None:
        self.assertTrue(is_normalized_id("feat:rfc.9000.connection-migration"))
        self.assertTrue(is_normalized_id("clm:rfc.9000.connection-migration.t3"))

    def test_rejects_non_normalized_ids(self) -> None:
        self.assertFalse(is_normalized_id("feat:RFC9000"))
        self.assertFalse(is_normalized_id("feat/rfc9000"))
        self.assertFalse(is_normalized_id("feature-no-prefix"))

    def test_filesystem_safe_projection(self) -> None:
        self.assertEqual(filesystem_safe_id("rel:1.2.0"), "rel__1.2.0")


if __name__ == "__main__":
    unittest.main()
