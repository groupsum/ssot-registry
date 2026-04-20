# Freeze Readiness

Freeze only when all of the following are true:

- target feature IDs are known
- feature planning fields are set
- profile IDs are either absent or intentionally included
- boundary scope is complete
- the user is no longer changing scope
- validation or inspection does not show a blocking scope problem

After freeze, implementation should satisfy the boundary instead of revising it.
