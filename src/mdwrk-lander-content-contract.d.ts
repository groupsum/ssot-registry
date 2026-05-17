declare module "@mdwrk/lander-content-contract" {
  export type PageKind =
    | "home"
    | "feature"
    | "use_case"
    | "answer"
    | "compare"
    | "package"
    | "proof"
    | "pricing"
    | "docs_bridge"
    | "trust";

  export type SectionKind =
    | "hero"
    | "feature_grid"
    | "feature_detail"
    | "comparison"
    | "proof_matrix"
    | "package_grid"
    | "pricing"
    | "cta"
    | "faq"
    | "markdown";

  export interface Cta {
    label: string;
    href: string;
    variant?: "primary" | "secondary" | "tertiary";
  }

  export interface FaqItem {
    question: string;
    answer: string;
  }

  export interface BaseSection {
    id: string;
    kind: SectionKind;
    title?: string;
  }

  export interface HeroSection extends BaseSection {
    kind: "hero";
    eyebrow?: string;
    title: string;
    subtitle: string;
    primaryCta?: Cta;
    secondaryCta?: Cta;
  }

  export interface FeatureGridSection extends BaseSection {
    kind: "feature_grid";
    title: string;
    items: Array<Record<string, unknown>>;
  }

  export interface ProofMatrixSection extends BaseSection {
    kind: "proof_matrix";
    title: string;
    items: Array<Record<string, unknown>>;
  }

  export interface PackageGridSection extends BaseSection {
    kind: "package_grid";
    title: string;
    packages: Array<Record<string, unknown>>;
  }

  export interface MarkdownSection extends BaseSection {
    kind: "markdown";
    body: string;
  }

  export interface CtaSection extends BaseSection {
    kind: "cta";
    title: string;
    body?: string;
    primaryCta?: Cta;
    secondaryCta?: Cta;
  }

  export interface ComparisonSection extends BaseSection {
    kind: "comparison";
    title: string;
    columns: Array<Record<string, unknown>>;
    rows: Array<Record<string, unknown>>;
  }

  export interface FaqSection extends BaseSection {
    kind: "faq";
    items: FaqItem[];
  }

  export type SectionSpec =
    | HeroSection
    | FeatureGridSection
    | ProofMatrixSection
    | PackageGridSection
    | MarkdownSection
    | CtaSection
    | ComparisonSection
    | FaqSection
    | (BaseSection & Record<string, unknown>);

  export interface PageSpec {
    kind: PageKind;
    slug: string;
    title: string;
    description: string;
    h1: string;
    intro: string;
    sections: SectionSpec[];
    faq?: FaqItem[];
    seo?: Record<string, unknown>;
    schema?: Array<Record<string, unknown>>;
    componentIntents?: Array<Record<string, unknown>>;
  }

  export interface SchemaSpec {
    [key: string]: unknown;
    id?: string;
    kind: string;
    data?: Record<string, unknown>;
  }

  export interface LanderSite {
    product: Record<string, unknown> & { name: string; slug: string; canonicalUrl: string };
    pages: PageSpec[];
    nav?: Record<string, unknown>;
    footer?: Record<string, unknown>;
    theme?: Record<string, unknown>;
    seo?: Record<string, unknown>;
    ai?: Record<string, unknown>;
  }
}
