# SSOT Registry site content pack audit

The site content pack is a generated content system: source modules define audiences, subjects, packages, APIs, sections, page plans, page specs, sitemap structure, discovery artifacts, and component traceability outputs.

## Corpus contract

- Formula: 12 sections * 20 subject areas * 4 intents * 4 audiences = 3840 pages
- Generated detail pages: 3840
- Section index pages: 12
- Primary groups: Features, Proof, Packages, FAQ

## Review lanes

### Technical Writer

Checked surfaces: editorial guidance, package/API copy, generated page body copy, homepage.

Findings:
- The pack already names .ssot/registry.json, ADRs, SPECs, features, claims, tests, evidence, boundaries, and releases as the canonical entity chain.
- The highest-risk copy is package and API guidance because it must stay aligned with real command behavior.

Upgrade actions:
- Keep boundary and release language distinct.
- Add command outputs and workflow stages to every related API detail.
- Keep package descriptions proof-led and technically defensible.

Acceptance criteria:
- Every related API has a description, output, and workflow stage.
- Every related package has install guidance, an audience fit, a proof point, and primary commands.

### Curriculum Planner

Checked surfaces: page plans, course pages, lesson pages, sitemap tree.

Findings:
- Course and lesson surfaces exist, but learning metadata needs to be explicit rather than implied by generated copy.
- The audience and intent matrix can support learning paths if prerequisites, outcomes, exercises, checkpoints, and next steps are generated consistently.

Upgrade actions:
- Add learner level, prerequisites, learning outcome, exercise, checkpoint, and next step to every page plan.
- Render these fields into course pages and non-course learning checkpoint sections.

Acceptance criteria:
- Course pages expose prerequisites, outcomes, exercises, and checkpoints.
- Lesson pages include a concrete exercise and next-step checkpoint.

### SEO, AEO, and AiEO Specialist

Checked surfaces: SEO fields, structured data, sitemap, llms.txt, semantic index.

Findings:
- Discovery infrastructure is strong: sitemap, robots, LLM files, content index, semantic index, and structured data graph are generated.
- The main quality risk is large-scale repetition across generated pages.

Upgrade actions:
- Add answer-first learning outcomes into descriptions and intros.
- Preserve schema and discovery completeness while avoiding visible implementation labels.

Acceptance criteria:
- Generated pages remain unique, routable, and represented in the formal sitemap tree.
- Discovery artifacts stay complete and rooted at the canonical ssot-registry.com URL.

### Technical Marketing Engineer

Checked surfaces: homepage, CTAs, package chooser, workflow copy, proof points.

Findings:
- The homepage is accurate, but the value proposition needs to emphasize the concrete developer outcome sooner.
- The package chooser should connect package roles to adoption tasks and proof points.

Upgrade actions:
- Add a first-five-minutes path for install, validate, and proof workflow discovery.
- Make package cards describe best fit, proof point, and primary command path.

Acceptance criteria:
- A developer can understand the product, install path, first command, and proof model from the homepage plus one click.
- Marketing claims remain tied to commands, registry entities, or generated artifacts.
