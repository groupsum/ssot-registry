# Verification

Executed successfully:

- `python -m pip install -e .`
- `python -m compileall src tests`
- `python -m build`

Verified test files:

Integration:
- `tests/integration/test_cli_boundary.py`
- `tests/integration/test_cli_claim.py`
- `tests/integration/test_cli_evidence.py`
- `tests/integration/test_cli_feature.py`
- `tests/integration/test_cli_graph.py`
- `tests/integration/test_cli_init.py`
- `tests/integration/test_cli_issue.py`
- `tests/integration/test_cli_release.py`
- `tests/integration/test_cli_release_flow.py`
- `tests/integration/test_cli_risk.py`
- `tests/integration/test_cli_test.py`
- `tests/integration/test_cli_validate.py`

Unit:
- `tests/unit/test_graph_export.py`
- `tests/unit/test_guards.py`
- `tests/unit/test_ids.py`
- `tests/unit/test_requires.py`
- `tests/unit/test_validate.py`

Current test inventory:

- 26 collected tests
- 26 passing when verified by file/group

Implemented CLI surfaces:

- `ssot-registry init`
- `ssot-registry validate`
- `ssot-registry feature create|get|list|update|delete|link|unlink|plan|lifecycle set`
- `ssot-registry test create|get|list|update|delete|link|unlink`
- `ssot-registry claim create|get|list|update|delete|link|unlink|evaluate|set-status|set-tier`
- `ssot-registry evidence create|get|list|update|delete|link|unlink|verify`
- `ssot-registry issue create|get|list|update|delete|link|unlink|plan|close|reopen`
- `ssot-registry risk create|get|list|update|delete|link|unlink|mitigate|accept|retire`
- `ssot-registry boundary create|get|list|update|delete|add-feature|remove-feature|freeze`
- `ssot-registry release create|get|list|update|delete|add-claim|remove-claim|add-evidence|remove-evidence|certify|promote|publish|revoke`
- `ssot-registry graph export`

Additional implemented behavior:

- feature `requires` dependencies
- `REQUIRES` graph edges
- required-feature passing checks
- required-feature cycle detection
