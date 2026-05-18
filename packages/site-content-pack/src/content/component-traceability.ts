import { sectionBlueprints } from "./sections.js";

export type RendererStatus = "direct" | "generic" | "schema-only";

export interface SsotComponentTraceabilityRow {
  ssotComponent: string;
  sections: string[];
  structuredDataTypes: string[];
  landerReactRenderers: string[];
  rendererStatus: RendererStatus;
  notes: string;
}

export interface LanderReactStructuredDataTraceabilityRow {
  structuredDataType: string;
  landerReactComponent: string;
  sharedStructuredDataBuilder: string;
  usedBySsotRegistry: boolean;
  ssotSections: string[];
  notes: string;
}

const ssotComponentRendererMap: Record<string, Pick<SsotComponentTraceabilityRow, "landerReactRenderers" | "rendererStatus" | "notes">> = {
  ApiReferenceBlock: {
    landerReactRenderers: ["PackageGrid", "MarkdownSectionView", "SoftwareSourceCodeStructuredData", "TechArticleStructuredData", "ItemListStructuredData"],
    rendererStatus: "generic",
    notes: "API reference content is represented as package-grid cards, explanatory text, and JSON-LD; lander-react does not yet expose a distinct ApiReferenceBlock visual renderer.",
  },
  Breadcrumbs: {
    landerReactRenderers: ["Breadcrumbs", "BreadcrumbList", "BreadcrumbListStructuredData"],
    rendererStatus: "direct",
    notes: "Breadcrumbs have both a visible lander-react renderer and BreadcrumbList JSON-LD support.",
  },
  CertificationPathBlock: {
    landerReactRenderers: ["PackageGrid", "ProofMatrix", "CourseStructuredData", "ClaimReviewStructuredData"],
    rendererStatus: "generic",
    notes: "Certification paths render through course, lesson, proof, and package sections until a dedicated certification visual block exists.",
  },
  ClaimReviewBlock: {
    landerReactRenderers: ["ProofMatrix", "ClaimReviewStructuredData"],
    rendererStatus: "generic",
    notes: "Claim review content is visible in proof matrices and emitted as ClaimReview JSON-LD.",
  },
  CodeExampleBlock: {
    landerReactRenderers: ["MarkdownSectionView", "PackageGrid", "SoftwareSourceCodeStructuredData", "TechArticleStructuredData"],
    rendererStatus: "generic",
    notes: "Code examples are carried in explanatory sections and command cards; schema maps to source-code and technical-article nodes.",
  },
  ComparisonMatrix: {
    landerReactRenderers: ["ComparisonMatrix"],
    rendererStatus: "direct",
    notes: "Comparison sections render through the lander-react comparison table.",
  },
  CourseBlock: {
    landerReactRenderers: ["FeatureGrid", "ComparisonMatrix", "PackageGrid", "FaqBlock", "CourseStructuredData", "CourseInstanceStructuredData"],
    rendererStatus: "generic",
    notes: "Course pages use multiple generic lander sections for metadata, lessons, and quizzes plus Course and CourseInstance JSON-LD.",
  },
  DatasetIndexBlock: {
    landerReactRenderers: ["PackageGrid", "ProofMatrix", "DatasetStructuredData"],
    rendererStatus: "generic",
    notes: "Dataset indexes are represented as evidence/proof cards and Dataset JSON-LD.",
  },
  DefinedTermSetBlock: {
    landerReactRenderers: ["PackageGrid", "FaqBlock", "TechArticleStructuredData"],
    rendererStatus: "schema-only",
    notes: "SSOT Registry declares DefinedTerm/DefinedTermSet in its model, but current lander-react JSON-LD support normalizes these pages to technical article style output.",
  },
  FAQPageBlock: {
    landerReactRenderers: ["FaqBlock", "FaqPage", "FAQPageStructuredData"],
    rendererStatus: "direct",
    notes: "FAQ content has a visible FAQ renderer and FAQPage JSON-LD support.",
  },
  FeatureGrid: {
    landerReactRenderers: ["FeatureGrid"],
    rendererStatus: "direct",
    notes: "Feature grids map directly to the lander-react FeatureGrid renderer.",
  },
  HowToBlock: {
    landerReactRenderers: ["FeatureGrid", "MarkdownSectionView", "HowToStructuredData"],
    rendererStatus: "generic",
    notes: "How-to content is visible as step-oriented grids or copy and emitted as HowTo JSON-LD.",
  },
  LessonBlock: {
    landerReactRenderers: ["PackageGrid", "MarkdownSectionView", "HowToStructuredData", "TechArticleStructuredData"],
    rendererStatus: "generic",
    notes: "Lessons render as course-linked cards and explanatory sections with HowTo or TechArticle JSON-LD.",
  },
  LessonListBlock: {
    landerReactRenderers: ["PackageGrid", "ItemListStructuredData"],
    rendererStatus: "generic",
    notes: "Lesson lists render as package-grid style linked cards and can be represented as ItemList JSON-LD.",
  },
  PackageGrid: {
    landerReactRenderers: ["PackageGrid"],
    rendererStatus: "direct",
    notes: "Package grid content maps directly to the lander-react PackageGrid renderer.",
  },
  ProofMatrix: {
    landerReactRenderers: ["ProofMatrix"],
    rendererStatus: "direct",
    notes: "Proof matrices map directly to the lander-react ProofMatrix renderer.",
  },
  QAPageBlock: {
    landerReactRenderers: ["FaqBlock", "FaqPage", "QAPageStructuredData"],
    rendererStatus: "generic",
    notes: "QA content reuses the visible FAQ renderer while preserving QAPage JSON-LD intent.",
  },
  RelatedApisBlock: {
    landerReactRenderers: ["PackageGrid", "ItemListStructuredData"],
    rendererStatus: "generic",
    notes: "Related API links render as linked cards and can be represented as ItemList JSON-LD.",
  },
  RelatedPackagesBlock: {
    landerReactRenderers: ["PackageGrid", "ProductStructuredData", "SoftwareApplicationStructuredData"],
    rendererStatus: "generic",
    notes: "Related package links reuse PackageGrid and product/software schema nodes.",
  },
  SoftwareApplicationBlock: {
    landerReactRenderers: ["PackageGrid", "SoftwareApplicationStructuredData"],
    rendererStatus: "generic",
    notes: "Software application content appears in package cards and SoftwareApplication JSON-LD.",
  },
  SoftwareSourceCodeBlock: {
    landerReactRenderers: ["PackageGrid", "MarkdownSectionView", "SoftwareSourceCodeStructuredData"],
    rendererStatus: "generic",
    notes: "Source-code content is visible in package/reference sections and emitted as SoftwareSourceCode JSON-LD.",
  },
  TechArticleBlock: {
    landerReactRenderers: ["MarkdownSectionView", "TechArticleStructuredData", "ArticleStructuredData"],
    rendererStatus: "generic",
    notes: "Technical article content renders through generic markdown or section copy and emits article-style JSON-LD.",
  },
  WorkflowBlock: {
    landerReactRenderers: ["FeatureGrid", "ProofMatrix", "HowToStructuredData", "ItemListStructuredData"],
    rendererStatus: "generic",
    notes: "Workflow pages use step/question grids and proof sections plus HowTo and ItemList JSON-LD.",
  },
};

export const ssotComponentTraceabilityMatrix: SsotComponentTraceabilityRow[] = Object.entries(ssotComponentRendererMap)
  .map(([ssotComponent, renderer]) => {
    const owningSections = sectionBlueprints.filter((section) => section.components.includes(ssotComponent as never));
    return {
      ssotComponent,
      sections: owningSections.map((section) => section.id),
      structuredDataTypes: [...new Set(owningSections.flatMap((section) => section.structuredDataTypes))],
      ...renderer,
    };
  })
  .sort((left, right) => left.ssotComponent.localeCompare(right.ssotComponent));

const usedStructuredDataTypes = new Set(sectionBlueprints.flatMap((section) => section.structuredDataTypes));

export const landerReactStructuredDataTraceabilityMatrix: LanderReactStructuredDataTraceabilityRow[] = [
  ["AggregateRating", "AggregateRatingStructuredData", "aggregateRatingNode"],
  ["Article", "ArticleStructuredData", "articleNode"],
  ["BlogPosting", "BlogPostingStructuredData", "blogPostingNode"],
  ["Book", "BookStructuredData", "bookNode"],
  ["BreadcrumbList", "BreadcrumbListStructuredData", "breadcrumbListSchema"],
  ["ClaimReview", "ClaimReviewStructuredData", "claimReviewNode"],
  ["Course", "CourseStructuredData", "courseNode"],
  ["CourseInstance", "CourseInstanceStructuredData", "courseInstanceNode"],
  ["Dataset", "DatasetStructuredData", "datasetNode"],
  ["DiscussionForumPosting", "DiscussionForumPostingStructuredData", "discussionForumPostingNode"],
  ["EmployerAggregateRating", "EmployerAggregateRatingStructuredData", "employerAggregateRatingNode"],
  ["Event", "EventStructuredData", "eventNode"],
  ["FAQPage", "FAQPageStructuredData", "faqPageSchema"],
  ["HowTo", "HowToStructuredData", "howToNode"],
  ["ImageObject", "ImageObjectStructuredData", "imageObjectSchema"],
  ["ItemList", "ItemListStructuredData", "itemListNode"],
  ["JobPosting", "JobPostingStructuredData", "jobPostingNode"],
  ["LocalBusiness", "LocalBusinessStructuredData", "localBusinessNode"],
  ["MathSolver", "MathSolverStructuredData", "mathSolverNode"],
  ["MemberProgram", "MemberProgramStructuredData", "loyaltyProgramNode"],
  ["MerchantReturnPolicy", "MerchantReturnPolicyStructuredData", "merchantReturnPolicyNode"],
  ["MonetaryAmountDistribution", "MonetaryAmountDistributionStructuredData", "estimatedSalaryNode"],
  ["Movie", "MovieStructuredData", "movieNode"],
  ["OfferShippingDetails", "OfferShippingDetailsStructuredData", "offerShippingDetailsNode"],
  ["Organization", "OrganizationStructuredData", "organizationNode"],
  ["Product", "ProductStructuredData", "productNode"],
  ["ProductGroup", "ProductGroupStructuredData", "productGroupNode"],
  ["ProfilePage", "ProfilePageStructuredData", "profilePageNode"],
  ["QAPage", "QAPageStructuredData", "qaPageSchema"],
  ["ReadAction", "ReadActionStructuredData", "readActionNode"],
  ["Recipe", "RecipeStructuredData", "recipeNode"],
  ["Review", "ReviewStructuredData", "reviewNode"],
  ["SoftwareApplication", "SoftwareApplicationStructuredData", "softwareApplicationNode"],
  ["SoftwareSourceCode", "SoftwareSourceCodeStructuredData", "softwareSourceCodeNode"],
  ["SpeakableSpecification", "SpeakableSpecificationStructuredData", "speakableSpecificationNode"],
  ["TechArticle", "TechArticleStructuredData", "techArticleNode"],
  ["VacationRental", "VacationRentalStructuredData", "vacationRentalNode"],
  ["Vehicle", "VehicleStructuredData", "vehicleListingNode"],
  ["VideoObject", "VideoObjectStructuredData", "videoObjectNode"],
  ["WebApplication", "WebApplicationStructuredData", "webApplicationNode"],
  ["WebPage", "WebPageStructuredData", "webPageSchema"],
  ["WebSite", "WebSiteStructuredData", "webSiteSchema"],
].map(([structuredDataType, landerReactComponent, sharedStructuredDataBuilder]) => {
  const ssotSections = sectionBlueprints
    .filter((section) => section.structuredDataTypes.includes(structuredDataType as never))
    .map((section) => section.id);
  const usedBySsotRegistry = ssotSections.length > 0;
  return {
    structuredDataType,
    landerReactComponent,
    sharedStructuredDataBuilder,
    usedBySsotRegistry,
    ssotSections,
    notes: usedBySsotRegistry
      ? "Used by the SSOT Registry content pack section model."
      : "Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections.",
  };
});
