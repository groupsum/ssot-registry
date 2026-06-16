import React from "react";
import { valueText } from "./format";

export function KeyValue({ record, keys }: { record?: Record<string, unknown>; keys?: string[] }): React.ReactElement {
  const entries = keys ? keys.map((key) => [key, record?.[key]] as const) : Object.entries(record || {});
  return (
    <div className="ssot-kv">
      {entries.map(([key, value]) => (
        <div className="ssot-kv-row" key={key}>
          <div className="ssot-kv-key">{key}</div>
          <div className="ssot-kv-value">{valueText(value)}</div>
        </div>
      ))}
    </div>
  );
}
