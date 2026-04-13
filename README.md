# ssot-registry

`ssot-registry` is a portable, repository-agnostic single-source-of-truth system for:

- features
- tests
- claims
- evidence
- issues
- risks
- frozen boundaries
- releases

The canonical machine-readable artifact is:

```text
.ssot/registry.json
```

Everything else is derived from it.

## Core model

- Features are the only targetable units.
- Features carry planning horizon and target claim tier.
- Claims assert properties of features.
- Tests verify claims.
- Evidence supports claims and is linked to tests.
- Issues and risks are plannable and can block certification, promotion, or publication.
- Boundaries freeze scope.
- Releases bundle claims and evidence against a frozen boundary.

## Canonical format

The canonical authored format is JSON. Markdown, CSV, DOT, SQLite, and reports are derived projections.

## CLI

```bash
ssot-registry init .
ssot-registry validate .
ssot-registry feature plan . --ids feat:example.bootstrap --horizon current --claim-tier T1
ssot-registry feature lifecycle set . --ids feat:example.bootstrap --stage deprecated --note "Superseded by v2"
ssot-registry issue plan . --ids iss:example.blocker --horizon next
ssot-registry claim evaluate . --claim-id clm:example.bootstrap.t1
ssot-registry evidence verify . --evidence-id evd:t1.example.bootstrap.bundle
ssot-registry boundary freeze . --boundary-id bnd:default
ssot-registry release certify . --release-id rel:0.1.0 --write-report
ssot-registry release promote . --release-id rel:0.1.0
ssot-registry release publish . --release-id rel:0.1.0
ssot-registry graph export . --format json
```

## Public operator surfaces

- Canonical JSON registry: `.ssot/registry.json`
- JSON Schema pack
- Noun-scoped CLI emitting JSON
- Python API under `ssot_registry.api`
- Derived graph, report, and snapshot artifacts

## Repository layout

See `docs/specs/file-tree.md` and the embedded examples under `docs/examples/`.

## Development

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```
