# SPEC-0614: Profile evaluation and boundary resolution

## Status
Draft

## Overview

Profiles are reusable bundles of features and/or nested profiles.

## Registry model

Top-level section:

- `profiles: []`

Profile row fields:

- `id`, `title`, `description`, `status`, `kind`
- `feature_ids: list[str]`
- `profile_ids: list[str]`
- `claim_tier: T0..T4 | null`
- `evaluation.mode = all_features_must_pass`
- `evaluation.allow_feature_override_tier: bool`

Boundary rows include:

- `feature_ids: list[str]`
- `profile_ids: list[str]`

## Evaluation

Feature pass criteria:

1. implemented status,
2. required features pass,
3. at least one linked claim passes claim-closure checks and meets required tier.

Required tier resolution:

1. feature target tier,
2. profile claim tier,
3. fail closed if neither is present.

Profile pass criteria:

- resolve transitive features from direct + nested profile references,
- evaluate each resolved feature,
- profile passes iff all resolved features pass.

## Boundary scope resolution

Resolved boundary features are computed dynamically:

1. start with direct boundary `feature_ids`,
2. expand all boundary `profile_ids` transitively,
3. dedupe while preserving first-seen order.

Stored boundary data is not rewritten during resolution.

