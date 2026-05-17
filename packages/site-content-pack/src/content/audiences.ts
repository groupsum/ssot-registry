export const audiences = [
  "Developer",
  "Architect",
  "Release manager",
  "Vibe coder",
] as const;

export type Audience = (typeof audiences)[number];
