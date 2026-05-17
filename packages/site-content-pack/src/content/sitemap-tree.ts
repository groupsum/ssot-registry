import type { PageSpec } from "@mdwrk/lander-content-contract";
import { generatedContentIndexPage, generatedCorpusPages, generatedSectionIndexPages } from "./page-corpus.js";
import { generatePagePlans, slugify } from "./page-plan.js";
import { sectionBlueprints, type SectionId } from "./sections.js";

export interface SitemapTreeNode {
  id: string;
  label: string;
  path: string;
  title: string;
  description: string;
  level: number;
  kind: "home" | "content-hub" | "primary-section" | "subsection" | "detail";
  sectionId?: SectionId;
  primarySectionId?: PrimarySectionId;
  pageCount: number;
  children: SitemapTreeNode[];
}

export type PrimarySectionId = "features" | "proof" | "packages" | "faq";

export interface PrimarySitemapSection {
  id: PrimarySectionId;
  label: string;
  path: string;
  description: string;
  subsectionIds: readonly SectionId[];
}

export const primarySitemapSections = [
  {
    id: "features",
    label: "Features",
    path: "/content/features/",
    description: "Features, workflows, and comparisons for the SSOT Registry model.",
    subsectionIds: ["Features", "Workflows", "Comparisons"],
  },
  {
    id: "proof",
    label: "Proof",
    path: "/content/proofs/",
    description: "Proof, certifications, courses, and lessons for release authority.",
    subsectionIds: ["Proofs", "Certifications", "Courses", "Lessons"],
  },
  {
    id: "packages",
    label: "Packages",
    path: "/content/packages/",
    description: "Packages, packs, and API references for operating the canonical registry.",
    subsectionIds: ["Packages", "Packs", "API_Reference"],
  },
  {
    id: "faq",
    label: "FAQ",
    path: "/content/faq-qa/",
    description: "FAQ, QA, and glossary answers for single source of truth concepts.",
    subsectionIds: ["FAQ_QA", "Glossary"],
  },
] as const satisfies readonly PrimarySitemapSection[];

const sectionToPrimary = new Map<SectionId, PrimarySectionId>(
  primarySitemapSections.flatMap((section) =>
    section.subsectionIds.map((subsectionId) => [subsectionId, section.id] as const),
  ),
);

const pageBySlug = new Map<PageSpec["slug"], PageSpec>([
  [generatedContentIndexPage.slug, generatedContentIndexPage],
  ...generatedSectionIndexPages.map((page) => [page.slug, page] as const),
  ...generatedCorpusPages.map((page) => [page.slug, page] as const),
]);

const plansBySection = new Map<SectionId, string[]>();
for (const plan of generatePagePlans()) {
  const sectionId = plan.section as SectionId;
  const slugs = plansBySection.get(sectionId) ?? [];
  slugs.push(plan.slug);
  plansBySection.set(sectionId, slugs);
}

export const ssotRegistrySitemapTree = buildSitemapTree();
export const sitemapTreePaths = flattenSitemapTree(ssotRegistrySitemapTree).map((node) => node.path);

export function buildSitemapTree(): SitemapTreeNode {
  const contentNode = nodeFromPage({
    id: "sitemap:content",
    page: generatedContentIndexPage,
    label: "Content",
    level: 1,
    kind: "content-hub",
    children: primarySitemapSections.map((primarySection) => primarySectionNode(primarySection, 2)),
  });

  return {
    id: "sitemap:home",
    label: "Home",
    path: "/",
    title: "SSOT Registry",
    description: "SSOT Registry homepage.",
    level: 0,
    kind: "home",
    pageCount: 1 + contentNode.pageCount,
    children: [contentNode],
  };
}

export function flattenSitemapTree(root: SitemapTreeNode): SitemapTreeNode[] {
  return [root, ...root.children.flatMap((child) => flattenSitemapTree(child))];
}

export function sitemapTreeJson(root: SitemapTreeNode = ssotRegistrySitemapTree) {
  return {
    product: "SSOT Registry",
    rootPath: root.path,
    pageCount: root.pageCount,
    primarySections: primarySitemapSections.map((section) => ({
      id: section.id,
      label: section.label,
      path: section.path,
      subsectionIds: [...section.subsectionIds],
    })),
    tree: root,
  };
}

function primarySectionNode(primarySection: PrimarySitemapSection, level: number): SitemapTreeNode {
  const primarySubsection = primarySection.subsectionIds[0];
  const page = pageBySlug.get(primarySection.path);
  if (!page) {
    throw new Error(`Missing primary sitemap page: ${primarySection.path}`);
  }

  const directDetailNodes = detailNodesForSection(primarySubsection, primarySection.id, level + 1);
  const subsectionNodes = primarySection.subsectionIds
    .slice(1)
    .map((sectionId) => subsectionNode(sectionId, primarySection.id, level + 1));

  return nodeFromPage({
    id: `sitemap:primary:${primarySection.id}`,
    page,
    label: primarySection.label,
    level,
    kind: "primary-section",
    primarySectionId: primarySection.id,
    sectionId: primarySubsection,
    description: primarySection.description,
    children: [...directDetailNodes, ...subsectionNodes],
  });
}

function subsectionNode(sectionId: SectionId, primarySectionId: PrimarySectionId, level: number): SitemapTreeNode {
  const section = sectionBlueprints.find((entry) => entry.id === sectionId);
  const path = `/content/${slugify(sectionId)}/`;
  const page = pageBySlug.get(path);
  if (!section || !page) {
    throw new Error(`Missing subsection sitemap page: ${sectionId}`);
  }
  return nodeFromPage({
    id: `sitemap:subsection:${slugify(sectionId)}`,
    page,
    label: section.label,
    level,
    kind: "subsection",
    primarySectionId,
    sectionId,
    children: detailNodesForSection(sectionId, primarySectionId, level + 1),
  });
}

function detailNodesForSection(sectionId: SectionId, primarySectionId: PrimarySectionId, level: number): SitemapTreeNode[] {
  return (plansBySection.get(sectionId) ?? []).map((path) => {
    const page = pageBySlug.get(path);
    if (!page) {
      throw new Error(`Missing sitemap detail page: ${path}`);
    }
    return nodeFromPage({
      id: `sitemap:detail:${path.replace(/^\/|\/$/g, "").replace(/\//g, ".")}`,
      page,
      label: page.title,
      level,
      kind: "detail",
      primarySectionId,
      sectionId,
      children: [],
    });
  });
}

function nodeFromPage(input: {
  id: string;
  page: Pick<PageSpec, "slug" | "title" | "description">;
  label: string;
  level: number;
  kind: SitemapTreeNode["kind"];
  primarySectionId?: PrimarySectionId;
  sectionId?: SectionId;
  description?: string;
  children: SitemapTreeNode[];
}): SitemapTreeNode {
  const pageCount = 1 + input.children.reduce((sum, child) => sum + child.pageCount, 0);
  return {
    id: input.id,
    label: input.label,
    path: input.page.slug,
    title: input.page.title,
    description: input.description ?? input.page.description,
    level: input.level,
    kind: input.kind,
    primarySectionId: input.primarySectionId,
    sectionId: input.sectionId,
    pageCount,
    children: input.children,
  };
}

export function primarySectionForPath(path: string): PrimarySectionId | undefined {
  const normalized = path.endsWith("/") ? path : `${path}/`;
  const section = sectionBlueprints.find((entry) => normalized.startsWith(`/${slugify(entry.id)}/`));
  return section ? sectionToPrimary.get(section.id) : undefined;
}
