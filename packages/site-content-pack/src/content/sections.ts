import type { StructuredDataBackedComponent } from "./components.js";
import type { StructuredDataType } from "./structured-data.js";

export interface SectionBlueprint {
  id: string;
  label: string;
  intents: readonly [string, string, string, string];
  components: readonly StructuredDataBackedComponent[];
  structuredDataTypes: readonly StructuredDataType[];
}

export const sectionBlueprints = [
  {
    id: "Features",
    label: "Features",
    intents: ["what-is", "how-to-use", "governance-value", "implementation-map"],
    components: ["FeatureGrid", "TechArticleBlock", "Breadcrumbs", "FAQPageBlock"],
    structuredDataTypes: ["WebPage", "TechArticle", "DefinedTerm", "BreadcrumbList"],
  },
  {
    id: "Proofs",
    label: "Proofs",
    intents: ["proof-claim", "evidence-chain", "certification-readiness", "failure-mode"],
    components: ["ProofMatrix", "ClaimReviewBlock", "DatasetIndexBlock", "Breadcrumbs"],
    structuredDataTypes: ["ClaimReview", "Dataset", "WebPage", "BreadcrumbList"],
  },
  {
    id: "Packages",
    label: "Packages",
    intents: ["package-overview", "install-guide", "api-entrypoint", "related-package"],
    components: ["PackageGrid", "SoftwareApplicationBlock", "SoftwareSourceCodeBlock", "RelatedPackagesBlock"],
    structuredDataTypes: ["SoftwareApplication", "SoftwareSourceCode", "Product", "ItemList"],
  },
  {
    id: "Packs",
    label: "Packs",
    intents: ["contract-pack", "document-pack", "reserved-range-pack", "immutable-pack"],
    components: ["RelatedPackagesBlock", "DatasetIndexBlock", "TechArticleBlock", "Breadcrumbs"],
    structuredDataTypes: ["Dataset", "Article", "SoftwareSourceCode", "BreadcrumbList"],
  },
  {
    id: "FAQ_QA",
    label: "FAQ / QA",
    intents: ["faq-answer", "qa-answer", "operator-answer", "reviewer-answer"],
    components: ["FAQPageBlock", "QAPageBlock", "Breadcrumbs", "RelatedApisBlock"],
    structuredDataTypes: ["FAQPage", "QAPage", "WebPage", "BreadcrumbList"],
  },
  {
    id: "Courses",
    label: "Courses",
    intents: ["course-overview", "learning-path", "prerequisite-map", "outcome-map"],
    components: ["CourseBlock", "LessonListBlock", "CertificationPathBlock", "Breadcrumbs"],
    structuredDataTypes: ["Course", "CourseInstance", "ItemList", "BreadcrumbList"],
  },
  {
    id: "Lessons",
    label: "Lessons",
    intents: ["lesson", "exercise", "worked-example", "assessment-prep"],
    components: ["LessonBlock", "HowToBlock", "CodeExampleBlock", "Breadcrumbs"],
    structuredDataTypes: ["LearningResource", "HowTo", "TechArticle", "BreadcrumbList"],
  },
  {
    id: "Certifications",
    label: "Certifications",
    intents: ["certification-path", "readiness-check", "proof-review", "credential-outcome"],
    components: ["CertificationPathBlock", "ClaimReviewBlock", "CourseBlock", "Breadcrumbs"],
    structuredDataTypes: ["EducationalOccupationalCredential", "Course", "ClaimReview", "BreadcrumbList"],
  },
  {
    id: "API_Reference",
    label: "API Reference",
    intents: ["command-reference", "api-reference", "schema-reference", "example-reference"],
    components: ["ApiReferenceBlock", "CodeExampleBlock", "SoftwareSourceCodeBlock", "RelatedApisBlock"],
    structuredDataTypes: ["SoftwareSourceCode", "TechArticle", "Code", "ItemList"],
  },
  {
    id: "Workflows",
    label: "Workflows",
    intents: ["decision-to-scope", "scope-to-freeze", "proof-to-certify", "promote-to-publish"],
    components: ["HowToBlock", "WorkflowBlock", "ProofMatrix", "Breadcrumbs"],
    structuredDataTypes: ["HowTo", "TechArticle", "ItemList", "BreadcrumbList"],
  },
  {
    id: "Comparisons",
    label: "Comparisons",
    intents: ["compare-approaches", "before-after", "registry-vs-docs", "manual-vs-governed"],
    components: ["ComparisonMatrix", "FAQPageBlock", "TechArticleBlock", "Breadcrumbs"],
    structuredDataTypes: ["WebPage", "ItemList", "FAQPage", "BreadcrumbList"],
  },
  {
    id: "Glossary",
    label: "Glossary",
    intents: ["definition", "term-context", "related-terms", "operator-vocabulary"],
    components: ["DefinedTermSetBlock", "QAPageBlock", "Breadcrumbs", "RelatedApisBlock"],
    structuredDataTypes: ["DefinedTerm", "DefinedTermSet", "QAPage", "BreadcrumbList"],
  },
] as const satisfies readonly SectionBlueprint[];

export type SectionId = (typeof sectionBlueprints)[number]["id"];
