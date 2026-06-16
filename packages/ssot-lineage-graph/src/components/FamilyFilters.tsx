import React from "react";

export function FamilyFilters({
  families,
  familyVisible,
  setFamilyVisible,
}: {
  families: string[];
  familyVisible: Record<string, boolean>;
  setFamilyVisible: React.Dispatch<React.SetStateAction<Record<string, boolean>>>;
}): React.ReactElement {
  const setAllFamilies = (visible: boolean) => {
    setFamilyVisible(Object.fromEntries(families.map((family) => [family, visible])));
  };

  return (
    <>
      <div className="ssot-chip-row">
        <button type="button" onClick={() => setAllFamilies(true)}>
          Show all
        </button>
        <button type="button" onClick={() => setAllFamilies(false)}>
          Hide all
        </button>
      </div>
      <div className="ssot-families">
        {families.map((family) => (
          <label key={family}>
            <input
              type="checkbox"
              checked={familyVisible[family] !== false}
              onChange={(event) => setFamilyVisible((next) => ({ ...next, [family]: event.target.checked }))}
            />
            {family}
          </label>
        ))}
      </div>
    </>
  );
}
