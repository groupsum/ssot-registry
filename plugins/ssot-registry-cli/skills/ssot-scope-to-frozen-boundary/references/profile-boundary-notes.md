# Profile Boundary Notes

Boundaries may include direct `feature_ids` and `profile_ids`.

When profiles are present:

- treat boundary scope as resolved dynamically
- confirm the user intends profile expansion instead of enumerating every feature directly
- avoid rewriting stored boundary rows just to materialize resolved features

See `SPEC-0614-profile-evaluation-and-boundary-resolution.yaml` when profile behavior matters.
