---
name: ssot-evidence
description: Manage evidence entities with full CLI coverage, including claim/test linkage and verification operations.
---

# SSOT Evidence

Use this skill for evidence-only operations.

## Command discipline

- Do not spend turns rediscovering syntax with `--help` during normal SSOT work. Use the command surface and examples in this skill directly.
- Pick one verified CLI rail for the repo (`ssot`, `ssot-registry`, `ssot-cli`, or `uv run ssot`) and reuse it consistently by substituting that rail into the examples below.
- Only inspect parser or help text when the user explicitly asks about the CLI surface or when observed runtime behavior contradicts the command patterns documented here.
## Command surface

- `evidence create|get|list|update|delete|link|unlink|verify`

## Workflow

1. Inspect evidence metadata, path, and links.
2. Update evidence status/path from real artifact outcomes.
3. Verify evidence and linked support integrity.

## Operating rules

- Evidence should point to concrete artifact paths produced by real verification runs.
- Keep claim/test links complete before release certification.
- If the request includes boundary/release lifecycle work, escalate to `$ssot-e2e-change-orchestrator`.

## Example

```powershell
ssot evidence get . --id evd:demo.login.pytest
ssot evidence update . --id evd:demo.login.pytest --status passed --evidence-path .ssot/reports/login-pytest.json
ssot evidence verify . --evidence-id evd:demo.login.pytest
```

