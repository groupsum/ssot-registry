# Lifecycle Order

Use this order unless the user explicitly asks for a partial flow:

1. Decision
2. ADR and SPEC authoring
3. Feature planning and target setting
4. Boundary creation and freeze
5. Frozen-scope delivery: runtime implementation plus required tests
6. Claim, test, and evidence completion
7. Release creation and certification
8. Promotion
9. Publication
10. Closure verification

Interpret freeze as freezing scope, not code state. Implementation may continue after freeze, but the frozen scope should not churn.
Post-freeze delivery may be code-first or tests-first. Either order is valid, but both the runtime implementation and required functional tests must exist before verification begins.
Required functional tests cover happy paths, unhappy paths, valid and invalid inputs, expected outputs, and observable behavior. Add performance and conformance tests when the user requests them, a feature requires them, or the target claim tier requires them.
Do not model `freeze -> verify`, `freeze -> proof`, or `freeze -> certify` as a direct path unless implementation, required tests, and evidence are already complete.
