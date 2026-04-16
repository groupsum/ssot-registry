# ADR-0012: Portable SSOT core with repo-specific evidence adapters

## Status
Draft

## Decision
The SSOT core contract governs and validates the registry graph. Repository-specific evidence generation is implemented outside the core (or through adapters) per repository.

## Consequences
- SSOT core behavior stays portable across repositories.
- Evidence generation can vary by repository without changing the core contract.
