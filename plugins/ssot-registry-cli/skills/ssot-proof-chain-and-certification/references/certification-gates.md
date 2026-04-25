# Certification Gates

Before certification, confirm:

- the release references a frozen boundary
- the frozen boundary has been implemented in code/schema/migrations/tests rather than merely frozen as intent
- boundary feature coverage exists through linked claims
- target tiers are met
- evidence is linked and verifiable
- feature implementation status is aligned with actual repo reality
- no certification guard failure is being ignored

After certification:

- promote only from `certified`
- publish only from `promoted`

Treat failures as blocking, not advisory.
