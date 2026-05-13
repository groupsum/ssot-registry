# npmctl Issue Feedback Report

Date: 2026-05-12
Repository: `groupsum/ssot-registry`
Context: public deployment of `ssot-registry.com` and `www.ssot-registry.com` to the `ssot-registry_lander` container through Nginx Proxy Manager

## Executive Summary

During repeated lander deployment and repair attempts, `npmctl` exposed a few operator-facing gaps that make safe recovery unnecessarily difficult:

1. unmanaged live proxy hosts are detected, but the recovery path is too brittle
2. certificate creation appears too tightly coupled to reconcile and adopt flows
3. transient and stale certificate-order failures are not classified well enough for automation
4. repeated repair attempts can risk unnecessary Let's Encrypt issuance churn and early rate-limit exhaustion

These issues matter because the operator is trying to repair a broken public endpoint, not create new production entropy. The current behavior makes it too easy for deploy retries or reconciliation attempts to cause certificate activity when the safer desired behavior is to reuse, adopt, or defer.

## Environment and Scenario

We were deploying a public lander whose Docker Compose service and container are both named `ssot-registry_lander`. The public domains:

- `ssot-registry.com`
- `www.ssot-registry.com`

should route to that container via Nginx Proxy Manager, targeting container port `80`.

The deployment workflow handled:

- local Docker Compose deploy
- DNS record setup
- `npmctl` desired-state generation
- `npmctl` plan, adopt, and apply steps
- public endpoint verification

The main production symptom at the start of the incident was that the public domains returned `502 Bad Gateway`.

## Issues Observed

### 1. Unmanaged existing proxy host is detected but not resolved gracefully

`npmctl plan` correctly reported that the desired proxy host conflicted with an existing live proxy host that had no `npmctl` ownership metadata.

Observed conflict shape:

- existing proxy host already present for `ssot-registry.com` and `www.ssot-registry.com`
- desired state wanted the same domains under `npmctl` ownership
- plan reported an unmanaged resource conflict instead of a low-risk reconciliation path

This is a normal real-world state. Teams often inherit manually-created NPM resources or resources created by older tooling. A plan result that can identify this is good; what is missing is a first-class graceful way to resolve it.

### 2. Adoption appears to trigger certificate work too early

When attempting to reconcile the unmanaged proxy host using `npmctl adopt`, the operation did not behave like a pure ownership reconciliation step. Instead, it triggered certificate-related behavior.

Observed failures included:

- `Another instance of Certbot is already running.`
- `No order for ID ...`

This suggests that adoption is not isolated from certificate side effects. That is a problem because adoption is exactly the kind of operation that operators need to be able to perform safely during repair work.

### 3. Certificate creation can be spammed too easily during repair flows

One of our strongest requirements is that certificate creation must not be easy to abuse or accidentally spam.

Current risk factors:

- repeated workflow dispatches while debugging
- retries after transient failures
- retries after unmanaged resource conflicts
- adopt/apply flows that appear willing to create or rotate certificate state during reconciliation

If `npmctl` initiates new issuance attempts too eagerly for the same domain set, operators can burn through Let's Encrypt limits quickly, especially when the system is already in a broken state and being actively repaired.

### 4. Error handling is not structured enough for reliable automation

The current failures surfaced as hard API errors, but the error model is not operator-friendly enough for workflow automation.

Examples:

- certbot lock contention is retryable
- stale or invalid ACME order state is likely not retryable without cleanup
- unmanaged proxy host conflict is not necessarily an error condition if the live host is otherwise compatible

Today, these cases are too close together from the perspective of a deploy workflow. They require custom log scraping and guesswork rather than structured classification.

### 5. Conflict handling is too binary for near-compatible live state

In our case, the live proxy host already existed on the target domains. The operator need was not to create an entirely new production surface. The need was to:

- adopt the existing host if compatible
- update only the fields that differ
- avoid unnecessary certificate churn
- verify that the public domains serve the intended app

`npmctl` currently feels too binary here:

- either the resource is already managed and easy
- or it is unmanaged and falls into a brittle path with side effects

There needs to be a middle path for unmanaged-but-compatible resources.

## Why This Is Operationally Risky

These issues produce two failure modes that reinforce each other:

1. the public service remains broken because reconciliation is too fragile
2. every repair attempt risks more certificate churn than necessary

That is especially dangerous during an outage or degraded-service incident. Operators need repair flows to become more conservative and more predictable as conflicts increase, not less.

## Requested npmctl Improvements

### 1. Separate adoption from mutation

`npmctl adopt` should support a mode that only attaches ownership metadata to compatible live resources and does not initiate certificate issuance or other unrelated side effects.

Desired behavior:

- adopt matching `proxy_host`
- preserve or reference existing compatible certificate state
- do not create a new certificate unless explicitly requested

### 2. Make certificate creation explicit, not implicit

We need a clearer operator contract for certificate behavior during plan, adopt, and apply.

Examples of helpful controls:

- `--no-create-certificates`
- `--reuse-existing-cert-only`
- `--certificate-mode=reuse`
- `--certificate-mode=create`
- `--certificate-mode=rotate`

The important point is that certificate creation should not happen implicitly during ownership reconciliation unless the operator asked for it.

### 3. Add issuance deduplication and anti-spam protection

For a given exact domain set, `npmctl` should avoid repeatedly initiating new certificate issuance when:

- an issuance attempt is already in flight
- a recent issuance just failed and a cooldown should apply
- an existing compatible certificate can be reused
- the failure state indicates cleanup is required before retry

This is the key requirement for preventing accidental certificate abuse and avoiding immediate rate-limit exhaustion.

### 4. Return structured conflict and failure classes

We need machine-readable error categories so automation can choose the right response without parsing free-form logs.

Examples:

- `unmanaged_proxy_host`
- `compatible_unmanaged_proxy_host`
- `certificate_missing`
- `certificate_inflight`
- `certificate_rate_limited`
- `certificate_order_stale`
- `certificate_backend_locked`
- `domain_conflict`

These categories should be available from `plan`, `adopt`, and `apply`.

### 5. Distinguish retryable from non-retryable failures

Not all failures should be handled the same way.

Examples:

- `Another instance of Certbot is already running.` should be flagged retryable
- `No order for ID ...` likely needs cleanup or stale-order resolution rather than blind retry

If `npmctl` exposed retry semantics directly, CI workflows could respond safely and consistently.

### 6. Add safe reconciliation modes for unmanaged but compatible resources

`npmctl` should support a first-class operator workflow for the common case where the live NPM resource already exists and mostly matches the desired state.

Useful safe modes would include:

- adopt compatible live proxy host without certificate mutation
- replace live proxy host only if fields materially differ
- bind desired proxy host to an existing compatible certificate
- dry-run exact reconciliation plan with side effects clearly labeled

### 7. Expose certificate-state inspection clearly

Operators need to answer these questions before deciding whether to retry:

- does a compatible certificate already exist for this domain set?
- is certificate issuance already in flight?
- did the last issuance leave a stale or broken order?
- can the existing certificate be reused safely?
- will the next apply attempt create a new order?

Without this, workflows are forced to guess.

## Concrete Acceptance Criteria

The following would materially improve deploy safety and operability for our use case:

1. An unmanaged existing proxy host can be adopted without certificate side effects.
2. Certificate creation is opt-in during reconciliation, not implicit.
3. Repeated deploy retries for the same domain set do not repeatedly initiate new certificate orders.
4. `npmctl` exposes structured conflict and certificate failure classes.
5. Retryable and non-retryable failures are clearly distinguished.
6. Compatible existing resources can be reused or adopted gracefully instead of forcing brittle repair behavior.

## Suggested Issue Breakdown for npmctl Team

If the npmctl team prefers separate issues rather than one umbrella report, this report naturally splits into:

1. adopt should not implicitly trigger certificate issuance
2. certificate issuance needs anti-spam and deduplication safeguards
3. plan/apply/adopt need structured conflict and failure classifications
4. unmanaged but compatible proxy hosts need a safe reconciliation path
5. certificate in-flight, stale-order, and reuse state need first-class inspection support

## Closing Note

The core issue is not that `npmctl` fails on obvious bad input. The problem is that it does not yet provide a sufficiently safe operator experience for production reconciliation, especially when public endpoints are already broken and the system is under active repair.

For this class of deployment tooling, graceful conflict handling and conservative certificate behavior are not optional polish. They are part of the safety contract.
