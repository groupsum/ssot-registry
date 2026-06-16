import React from "react";
import { valueText } from "./format";

export function StatCard({ value, label }: { value: unknown; label: string }): React.ReactElement {
  return (
    <div className="ssot-stat">
      <b>{valueText(value)}</b>
      <span>{label}</span>
    </div>
  );
}
