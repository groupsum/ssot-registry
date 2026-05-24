# Content-Addressed Evidence Registry Truth Matrices

This note evaluates the provided diagram against the actual `ssot-registry` model and implementation in this checkout.

It is not a generic opinion about the graphic. It is a repo-grounded truth check.

## Scope

The diagram makes claims about:

- the entity model
- release and certification flow
- hashing and content addressing
- provenance and attestations
- immutability and verification properties

This document separates:

- what is clearly supported
- what is partially supported or weaker than shown
- what is not implemented in this repo
- what is overstated or misleading if read literally

## Emoji Legend

- `✅` supported
- `🟡` partial or weaker than shown
- `❌` not supported
- `⚠️` overstated or misleading

## Compact Support Matrix

| Detail | Support |
|---|---|
| Feature -> Claim -> Test -> Evidence model | ✅ |
| Canonical registry as source of truth | ✅ |
| Derived graph export | ✅ |
| Boundaries freeze scope | ✅ |
| Releases bundle claims and evidence | ✅ |
| Certification gate | ✅ |
| Promotion and publication gates | ✅ |
| Snapshot artifacts for releases | ✅ |
| SHA-256 hashing on docs, artifacts, and snapshots | ✅ |
| Local verification report | ✅ |
| Deterministic root hash | ✅ |
| Content-addressed framing | 🟡 |
| Tamper detection | 🟡 |
| Immutable snapshots | 🟡 |
| Merkle root or Merkle tree | ❌ |
| In-toto attestations | ❌ |
| SLSA provenance | ❌ |
| SBOM or CycloneDX | ❌ |
| Immutable vault | ❌ |
| Append-only registry | ❌ |
| "Evidence registry" as the whole system | ⚠️ |
| "Verifiable anywhere" | ⚠️ |
| "Trusted" or "cryptographically secured" as a full trust chain | ⚠️ |

## Matrix 1: High-Level Truth Status

| Topic | Image Claim | Repo Reality | Status |
|---|---|---|---|
| Canonical graph exists | Claims and evidence closure graph | Yes, derived from canonical `.ssot/registry.json` | ✅ |
| Feature, claim, test, evidence chain | Feature -> claim -> test -> evidence | Yes, this is a real core model | ✅ |
| Boundaries and releases | Frozen scope and release packaging | Yes, real boundary and release entities and gates | ✅ |
| Certification, promotion, publication | CI-like gated release lifecycle | Yes, implemented | ✅ |
| Graph export | Registry graph visualization and export | Yes, implemented | ✅ |
| Hash-based integrity | `sha256` on artifacts and snapshots | Yes, real in several surfaces | ✅ |
| "Evidence registry" as full label | System is mainly an evidence registry | No, the repo is broader than evidence | ⚠️ |
| Merkle root | Central Merkle root over the graph | No clear Merkle tree implementation; deterministic root hash exists | 🟡 |
| In-toto attestations | In-toto statements | Not found as an implemented repo surface | ❌ |
| SLSA provenance | SLSA provenance or levels | Not found as an implemented repo surface | ❌ |
| SBOM or CycloneDX | SBOM registry and release artifacts | Not found as an implemented repo surface | ❌ |
| Immutable vault | Vault-like immutable storage system | Not a real repo concept or surface | ❌ |
| Append-only records | Registry behaves append-only | No, CRUD and unlink or revoke operations exist | ❌ |
| Verifiable anywhere | Universal independent verification | Too strong for current implementation | ⚠️ |
| Cryptographically trusted | Strong signed trust chain implied | Too strong; hash verification exists, not a full trust fabric | ⚠️ |

## Matrix 2: What Is Actually Implemented

| Surface | In Repo | Notes |
|---|---|---|
| Features | Yes | Targetable units |
| Claims | Yes | Assertions about features |
| Tests | Yes | Verification procedures |
| Evidence | Yes | Artifacts and results linked into the proof chain |
| Issues | Yes | Can be release-blocking |
| Risks | Yes | Can be release-blocking |
| Boundaries | Yes | Freeze scope |
| Releases | Yes | Bundle claims and evidence against frozen boundaries |
| ADRs | Yes | Governed docs with `content_sha256` |
| Specs | Yes | Governed docs with `content_sha256` |
| Graph export | Yes | JSON, DOT, and PNG export surfaces |
| Certification report | Yes | Real release certification report |
| Promotion snapshot | Yes | Real snapshot output |
| Publication snapshot | Yes | Real snapshot output |
| Local release verification | Yes | `release verify-local` exists |
| Deterministic source root hash | Yes | Built from a canonical file-hash map |
| Artifact manifest hashing | Yes | Real `sha256` validation |
| Merkle tree | No clear implementation | Root hash is not presented as a tree structure |
| In-toto, SLSA, SBOM | No implemented surface found | The image appears aspirational or invented here |

## Matrix 3: Precise Interpretation of the Hashing Story

| Image Concept | Closest Repo Equivalent | Match Quality |
|---|---|---|
| Content-addressed nodes | `sha256` on governed docs, artifacts, and snapshots | 🟡 |
| Merkle root | Deterministic root hash of a file-hash map | 🟡 |
| Immutable snapshot bundle | Boundary, release, and published snapshots | ✅ |
| Tamper detection | Hash mismatch and local verification report | ✅ |
| Provenance bundle | Local evidence bundle | 🟡 |
| Attestation set | Local verification artifacts | 🟡 |
| Supply-chain transparency log | None clearly implemented | ❌ |

## Matrix 4: Strong vs Weak Claims

| Claim Strength | Safe to Say | Unsafe to Say |
|---|---|---|
| Safe | The repo models features, claims, tests, evidence, boundaries, and releases in one canonical registry. |  |
| Safe | It supports hash-based integrity and derived snapshots. |  |
| Safe | It can verify a local release bundle and detect drift in governed files. |  |
| Caution | It is content-addressed. | Only if clarified to mean hash-based artifacts and docs, not a full content-addressable storage architecture. |
| Caution | It has a root hash. | Only if clarified to mean deterministic hashing, not necessarily a Merkle structure. |
| Unsafe |  | It implements in-toto attestations. |
| Unsafe |  | It provides SLSA provenance. |
| Unsafe |  | It manages SBOM or CycloneDX artifacts. |
| Unsafe |  | It is append-only. |
| Unsafe |  | It is universally trust-verifiable anywhere. |

## Matrix 5: Image Cleanup Recommendations

| Image Element | Keep | Change |
|---|---|---|
| Feature, claim, test, evidence ladder | Yes | Keep |
| Boundary and release lifecycle | Yes | Keep |
| Hash and snapshot framing | Yes | Rename "Merkle root" to "deterministic root hash" |
| Evidence bundle | Yes | Keep, but call it "local evidence bundle" |
| CI or CD artifact panel | Maybe | Present as example inputs, not guaranteed built-in surfaces |
| Attestations panel | No | Replace with "local verification artifacts" unless those surfaces are implemented |
| Immutable vault | No | Remove or relabel as "published snapshot store" |
| Append-only or verifiable anywhere language | No | Soften to "hash-verifiable" and "locally verifiable" |

## Explanation

### What the image gets right

The image is directionally correct about the central SSOT graph shape.

This repo really does model:

- features
- claims
- tests
- evidence
- boundaries
- releases

It also really does provide:

- release certification
- promotion
- publication
- graph export
- snapshot artifacts
- hash-based integrity checks

That means the graphic is not pure fiction. It is anchored to several real concepts in this codebase.

### What the image strengthens beyond the repo

The graphic becomes misleading when it moves from "hash-based governed release verification" to "full content-addressed supply-chain attestation platform."

The repo does support a deterministic local root hash and local evidence bundle generation. But that is not the same thing as:

- a Merkle tree implementation
- in-toto statements
- SLSA provenance
- SBOM or CycloneDX generation
- a transparency log
- a vault-backed immutable storage system

Those ideas may be visually adjacent to the repo's current direction, but they are not honestly represented as implemented features in this checkout.

### Why "content-addressed" is only partial

The repo does use hashes in meaningful ways:

- ADR and SPEC documents carry `content_sha256`
- snapshots hash registry state and related artifacts
- local verification computes file hashes
- local assurance computes a deterministic root hash over a canonical file-hash map

That is enough to justify hash-oriented language.

It is not enough to justify a literal Merkle-tree or full content-addressable-storage claim unless that terminology is narrowed and explained.

### Why "append-only" is false

This repo is not append-only.

Its CLI and APIs support create, update, delete, link, unlink, and revoke operations across multiple entity families. The working registry is mutable until boundary freeze and release-state transitions constrain specific flows.

So append-only language is inaccurate for the registry as a whole.

### Why "verifiable anywhere" and "trusted" are too strong

The repo supports local verification of governed files and release artifacts. That is real.

But the image language suggests a stronger trust story:

- portable third-party independent verification
- signed attestation ecosystems
- global transparency or provenance standards
- a broader cryptographic trust chain

That stronger story is not what this checkout currently implements.

## Bottom Line

The honest summary is:

- the SSOT entity graph is real
- the release gates are real
- the hash and snapshot mechanisms are real
- the supply-chain attestation stack shown in the image is not real in this repo

If this graphic is reused, it should either:

- be softened to match current implementation truth, or
- be treated as a future-state concept graphic rather than a literal current-state architecture diagram
