# SPEC-0015: Profile evaluation and boundary resolution

## Summary
Profiles bundle direct `feature_ids` and nested `profile_ids`. Boundaries can reference `profile_ids` in addition to direct `feature_ids`.

## Rules
1. Required feature tier resolution is fail-closed:
   - feature `plan.target_claim_tier`
   - else profile `claim_tier`
   - else failure
2. Profile evaluation mode is `all_features_must_pass`.
3. Boundary semantic feature scope is resolved dynamically from direct features plus transitive profile expansion.
4. Stored boundary rows are not expanded on write.

## Outputs
Reports and graph exports include profile composition and boundary-to-profile scope edges.
