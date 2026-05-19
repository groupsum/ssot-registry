from __future__ import annotations

import unittest

from ssot_registry.validators.feature_parent_links import validate_feature_parent_links
from ssot_registry.validators.identity import build_index


class FeatureParentLinkValidationTests(unittest.TestCase):
    def test_rejects_self_parent_duplicate_and_cycle_links(self) -> None:
        registry = {
            "features": [
                {"id": "feat:demo.parent", "parent_feature_ids": ["feat:demo.child"]},
                {"id": "feat:demo.child", "parent_feature_ids": ["feat:demo.parent", "feat:demo.parent"]},
                {"id": "feat:demo.self", "parent_feature_ids": ["feat:demo.self"]},
            ]
        }
        failures: list[str] = []
        index = build_index(registry, failures)

        validate_feature_parent_links(index, failures)

        self.assertTrue(any("features.feat:demo.self.parent_feature_ids must not include itself" in failure for failure in failures))
        self.assertTrue(any("features.feat:demo.child.parent_feature_ids contains duplicate ids" in failure for failure in failures))
        self.assertTrue(any("Feature parent cycle detected:" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
