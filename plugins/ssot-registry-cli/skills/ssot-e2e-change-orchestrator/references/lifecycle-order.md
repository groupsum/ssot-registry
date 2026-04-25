# Lifecycle Order

Use this order unless the user explicitly asks for a partial flow:

1. Decision
2. ADR and SPEC authoring
3. Feature planning and target setting
4. Boundary creation and freeze
5. Implementation and migration delivery
6. Claim, test, and evidence completion
7. Release creation and certification
8. Promotion
9. Publication
10. Closure verification

Interpret freeze as freezing scope, not code state. Implementation may continue after freeze, but the frozen scope should not churn.
Do not model `freeze -> certify` as a direct path unless the implementation and verification phases are already complete and evidenced.
