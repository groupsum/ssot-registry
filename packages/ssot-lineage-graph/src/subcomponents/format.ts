export function valueText(value: unknown): string {
  if (Array.isArray(value)) {
    return value.length ? value.map(valueText).join(", ") : "none";
  }
  if (value && typeof value === "object") {
    return Object.entries(value as Record<string, unknown>)
      .map(([key, nested]) => `${key}: ${valueText(nested)}`)
      .join("; ");
  }
  return value === "" || value == null ? "none" : String(value);
}
