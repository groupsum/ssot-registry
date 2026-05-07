# Certification Gates

Before certification, confirm:

- the release references a frozen boundary
- the frozen boundary has been implemented in runtime code/schema/migrations/tests rather than merely frozen as intent
- code-first and tests-first delivery both converged before verification began
- required functional tests cover happy paths, unhappy paths, valid and invalid inputs, expected outputs, and observable behavior
- required performance and conformance tests exist when requested by the user, required by a feature, or required by the target claim tier
- boundary feature coverage exists through linked claims
- target tiers are met
- evidence is linked and verifiable
- feature implementation status is aligned with actual repo reality
- no certification guard failure is being ignored

After certification:

- promote only from `certified`
- publish only from `promoted`

Treat failures as blocking, not advisory.
