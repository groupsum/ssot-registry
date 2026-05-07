# Test Coverage Notes

Choose the narrowest combination of tests that proves the frozen scope:

- unit tests for pure model or guard logic
- integration tests for CLI or API flows
- migration tests for schema-version upgrades
- functional tests for happy paths, unhappy paths, valid and invalid inputs, expected outputs, and observable behavior
- performance tests when requested by the user, required by a feature, or required by the target claim tier
- conformance tests when requested by the user, required by a feature, or required by the target claim tier
- checked-in report or schema fixture updates when outputs are part of the contract

Code-first and tests-first are both valid. Verification starts only after both the runtime implementation and required tests exist.
Keep feature implementation status aligned with the observed test reality.
