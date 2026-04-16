# ADR-0014: Profiles are reusable feature bundles with derived pass status

## Status
Accepted

## Context
Boundaries are release-scope artifacts, but teams also need reusable capability bundles that can be shared across boundaries and deployments.

## Decision
Introduce `profiles` as first-class entities that aggregate features and nested profiles. Profile pass/fail state is derived at evaluation time and is not persisted in the registry.

## Consequences
- Profiles can be reused across boundaries and reports.
- Certification and coverage can reason over resolved profile feature scope.
- Persisted registry state remains canonical and non-derived.
