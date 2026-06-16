import type { LineageFamily } from "./types";

export const FAMILY_COLORS: Record<string, string> = {
  ADR: "#7c3aed",
  Boundary: "#0891b2",
  Claim: "#b45309",
  Evidence: "#64748b",
  Feature: "#0f766e",
  Issue: "#e11d48",
  Profile: "#9333ea",
  Release: "#16a34a",
  Risk: "#ea580c",
  Spec: "#2563eb",
  Test: "#dc2626",
};

export const FAMILY_RANKS: Record<string, number> = {
  ADR: 0,
  Spec: 1,
  Feature: 2,
  Claim: 3,
  Test: 4,
  Evidence: 5,
  Boundary: 6,
  Profile: 7,
  Release: 8,
  Issue: 9,
  Risk: 10,
};

export function familyColor(family: LineageFamily): string {
  return FAMILY_COLORS[String(family)] ?? "#475569";
}

export function familyRank(family: LineageFamily): number {
  return FAMILY_RANKS[String(family)] ?? 99;
}

export function familyClassName(family: LineageFamily): string {
  return `ssot-family-${String(family).toLowerCase().replace(/[^a-z0-9]+/g, "-")}`;
}
