# Test Coverage Notes

Choose the narrowest combination of tests that proves the frozen scope:

- unit tests for pure model or guard logic
- integration tests for CLI or API flows
- migration tests for schema-version upgrades
- checked-in report or schema fixture updates when outputs are part of the contract

Keep feature implementation status aligned with the observed test reality.
