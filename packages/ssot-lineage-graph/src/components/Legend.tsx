import React from "react";
import { familyClassName } from "../constants";

export function Legend({ families }: { families: string[] }): React.ReactElement {
  return (
    <div className="ssot-legend">
      {families.map((family) => (
        <div className="ssot-legend-item" key={family}>
          <span className={`ssot-swatch ${familyClassName(family)}`} />
          <span>{family}</span>
        </div>
      ))}
    </div>
  );
}
