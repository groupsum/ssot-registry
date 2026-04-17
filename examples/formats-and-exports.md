# Formats and exports example

This example shows how to render CLI responses in alternate formats and export durable artifacts for registry and graph data.

## 1) Render list commands in multiple formats

```bash
# YAML output to stdout
ssot-registry --output-format yaml feature list .

# CSV output to stdout
ssot-registry --output-format csv claim list .

# Table/DF-style output
ssot-registry --output-format df test list .

# Save rendered output to a file
ssot-registry --output-format csv --output-file .ssot/exports/features.csv feature list .
```

## 2) Export full registry document

```bash
# Export canonical data in different derived formats
ssot-registry registry export . --format json --output .ssot/exports/registry.json
ssot-registry registry export . --format yaml --output .ssot/exports/registry.yaml
ssot-registry registry export . --format toml --output .ssot/exports/registry.toml
```

## 3) Export graph as machine-readable, source, and images

```bash
# Graph as JSON
ssot-registry graph export . --format json --output .ssot/graphs/registry.graph.json

# Graphviz source (DOT)
ssot-registry graph export . --format dot --output .ssot/graphs/registry.graph.dot

# Rendered images (requires `dot` from Graphviz in PATH)
ssot-registry graph export . --format png --output .ssot/graphs/registry.graph.png
ssot-registry graph export . --format svg --output .ssot/graphs/registry.graph.svg
```

## 4) Validate generated artifacts

```bash
# quick checks
ls .ssot/exports
ls .ssot/graphs
```
