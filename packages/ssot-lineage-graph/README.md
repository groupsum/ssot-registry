# @ssot-registry/lineage-graph

Portable React viewer for SSOT lineage graph payloads.

```tsx
import { LineageGraphApp } from "@ssot-registry/lineage-graph";

<LineageGraphApp payload={payload} />;
```

The package also exports `createStandaloneHtml(payload)`, which is used by the Python `ssot-registry graph lineage` command to emit an offline HTML artifact.
