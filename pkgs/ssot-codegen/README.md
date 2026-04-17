<div align="center">
  <h1>🔷 ssot-codegen</h1>
  <p><strong>Development-time generators for SSOT contract-side metadata artifacts.</strong></p>
</div>

<div align="center">
  <a href="https://pypi.org/project/ssot-codegen/"><img src="https://img.shields.io/pypi/v/ssot-codegen?label=PyPI%20version" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/ssot-codegen/"><img src="https://img.shields.io/pypi/pyversions/ssot-codegen?label=Python" alt="Supported Python versions" /></a>
  <a href="https://pepy.tech/project/ssot-codegen"><img src="https://static.pepy.tech/badge/ssot-codegen" alt="Downloads" /></a>
  <a href="https://hits.sh/github.com/groupsum/ssot-registry/"><img src="https://hits.sh/github.com/groupsum/ssot-registry.svg?style=flat-square" alt="Repository hits" /></a>
</div>

`ssot-codegen` contains generators for SSOT contract-side metadata artifacts.

It is a development-oriented package used to materialize generated JSON and Python outputs from the canonical contract layer. It is not the main runtime entry point for end users.

## What this package owns

- The `ssot-codegen` console command
- Generation of Python-side metadata artifacts derived from `ssot-contracts`
- Development-time regeneration of CLI and TUI metadata outputs

## When to use this package

Use `ssot-codegen` when you want:

- to regenerate packaged metadata artifacts during development
- to inspect the current generated contract index, CLI metadata, or TUI metadata
- a small development utility around the canonical contract package

Use another package when you want:

- `ssot-cli` for the main user-facing CLI
- `ssot-registry` for the core runtime and Python APIs
- `ssot-contracts` for the packaged artifacts themselves
- `ssot-tui` for terminal UI access
- `ssot-views` for report and graph builders

## Install

```bash
python -m pip install ssot-codegen
```

For local development from this repository:

```bash
python -m pip install -e pkgs/ssot-codegen
```

## Command-line usage

The current command surface is intentionally small:

```bash
ssot-codegen --help
ssot-codegen --output-root .tmp_codegen
```

`--output-root` controls the directory where generated files are written. If omitted, the command writes to a `.tmp_codegen` directory under the current working directory.

## Generated outputs

`generate_python_artifacts()` currently writes:

- `contracts.index.json`
- `cli.metadata.json`
- `tui.metadata.json`
- `enums.py`
- `cli_metadata.py`
- `tui_metadata.py`

Example:

```bash
ssot-codegen --output-root .tmp_codegen
```

Typical output files and purpose:

- `contracts.index.json`: schema version and packaged ADR/spec manifest identifiers
- `cli.metadata.json`: output formats and entity sections used by CLI-facing tooling
- `tui.metadata.json`: entity sections used by TUI-facing tooling
- `enums.py`: generated Python constants derived from `CONTRACT_DATA`

## Programmatic usage

```python
from ssot_codegen.generator import generate_python_artifacts

written = generate_python_artifacts(".tmp_codegen")
for path in written:
    print(path.as_posix())
```

## Package relationships

- Package type: development/code-generation package
- Depends on: `ssot-contracts`, `ssot-views`
- Consumed by: maintainers and release tooling that regenerate derived metadata artifacts

If you are using SSOT as an application or library, you usually do not need this package directly. It is primarily for maintainers working on the SSOT workspace itself.
