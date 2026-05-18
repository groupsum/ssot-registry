# SSOT Registry component traceability matrix

Generated from `packages/site-content-pack/src/content/component-traceability.ts`.

## SSOT Registry components to lander-react renderers

| SSOT component | Sections | Structured data types | Lander React renderers | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| ApiReferenceBlock | API_Reference | SoftwareSourceCode, TechArticle, Code, ItemList | PackageGrid, MarkdownSectionView, SoftwareSourceCodeStructuredData, TechArticleStructuredData, ItemListStructuredData | generic | API reference content is represented as package-grid cards, explanatory text, and JSON-LD; lander-react does not yet expose a distinct ApiReferenceBlock visual renderer. |
| Breadcrumbs | Features, Proofs, Packs, FAQ_QA, Courses, Lessons, Certifications, Workflows, Comparisons, Glossary | WebPage, TechArticle, DefinedTerm, BreadcrumbList, ClaimReview, Dataset, Article, SoftwareSourceCode, FAQPage, QAPage, Course, CourseInstance, ItemList, LearningResource, HowTo, EducationalOccupationalCredential, DefinedTermSet | Breadcrumbs, BreadcrumbList, BreadcrumbListStructuredData | direct | Breadcrumbs have both a visible lander-react renderer and BreadcrumbList JSON-LD support. |
| CertificationPathBlock | Courses, Certifications | Course, CourseInstance, ItemList, BreadcrumbList, EducationalOccupationalCredential, ClaimReview | PackageGrid, ProofMatrix, CourseStructuredData, ClaimReviewStructuredData | generic | Certification paths render through course, lesson, proof, and package sections until a dedicated certification visual block exists. |
| ClaimReviewBlock | Proofs, Certifications | ClaimReview, Dataset, WebPage, BreadcrumbList, EducationalOccupationalCredential, Course | ProofMatrix, ClaimReviewStructuredData | generic | Claim review content is visible in proof matrices and emitted as ClaimReview JSON-LD. |
| CodeExampleBlock | Lessons, API_Reference | LearningResource, HowTo, TechArticle, BreadcrumbList, SoftwareSourceCode, Code, ItemList | MarkdownSectionView, PackageGrid, SoftwareSourceCodeStructuredData, TechArticleStructuredData | generic | Code examples are carried in explanatory sections and command cards; schema maps to source-code and technical-article nodes. |
| ComparisonMatrix | Comparisons | WebPage, ItemList, FAQPage, BreadcrumbList | ComparisonMatrix | direct | Comparison sections render through the lander-react comparison table. |
| CourseBlock | Courses, Certifications | Course, CourseInstance, ItemList, BreadcrumbList, EducationalOccupationalCredential, ClaimReview | FeatureGrid, ComparisonMatrix, PackageGrid, FaqBlock, CourseStructuredData, CourseInstanceStructuredData | generic | Course pages use multiple generic lander sections for metadata, lessons, and quizzes plus Course and CourseInstance JSON-LD. |
| DatasetIndexBlock | Proofs, Packs | ClaimReview, Dataset, WebPage, BreadcrumbList, Article, SoftwareSourceCode | PackageGrid, ProofMatrix, DatasetStructuredData | generic | Dataset indexes are represented as evidence/proof cards and Dataset JSON-LD. |
| DefinedTermSetBlock | Glossary | DefinedTerm, DefinedTermSet, QAPage, BreadcrumbList | PackageGrid, FaqBlock, TechArticleStructuredData | schema-only | SSOT Registry declares DefinedTerm/DefinedTermSet in its model, but current lander-react JSON-LD support normalizes these pages to technical article style output. |
| FAQPageBlock | Features, FAQ_QA, Comparisons | WebPage, TechArticle, DefinedTerm, BreadcrumbList, FAQPage, QAPage, ItemList | FaqBlock, FaqPage, FAQPageStructuredData | direct | FAQ content has a visible FAQ renderer and FAQPage JSON-LD support. |
| FeatureGrid | Features | WebPage, TechArticle, DefinedTerm, BreadcrumbList | FeatureGrid | direct | Feature grids map directly to the lander-react FeatureGrid renderer. |
| HowToBlock | Lessons, Workflows | LearningResource, HowTo, TechArticle, BreadcrumbList, ItemList | FeatureGrid, MarkdownSectionView, HowToStructuredData | generic | How-to content is visible as step-oriented grids or copy and emitted as HowTo JSON-LD. |
| LessonBlock | Lessons | LearningResource, HowTo, TechArticle, BreadcrumbList | PackageGrid, MarkdownSectionView, HowToStructuredData, TechArticleStructuredData | generic | Lessons render as course-linked cards and explanatory sections with HowTo or TechArticle JSON-LD. |
| LessonListBlock | Courses | Course, CourseInstance, ItemList, BreadcrumbList | PackageGrid, ItemListStructuredData | generic | Lesson lists render as package-grid style linked cards and can be represented as ItemList JSON-LD. |
| PackageGrid | Packages | SoftwareApplication, SoftwareSourceCode, Product, ItemList | PackageGrid | direct | Package grid content maps directly to the lander-react PackageGrid renderer. |
| ProofMatrix | Proofs, Workflows | ClaimReview, Dataset, WebPage, BreadcrumbList, HowTo, TechArticle, ItemList | ProofMatrix | direct | Proof matrices map directly to the lander-react ProofMatrix renderer. |
| QAPageBlock | FAQ_QA, Glossary | FAQPage, QAPage, WebPage, BreadcrumbList, DefinedTerm, DefinedTermSet | FaqBlock, FaqPage, QAPageStructuredData | generic | QA content reuses the visible FAQ renderer while preserving QAPage JSON-LD intent. |
| RelatedApisBlock | FAQ_QA, API_Reference, Glossary | FAQPage, QAPage, WebPage, BreadcrumbList, SoftwareSourceCode, TechArticle, Code, ItemList, DefinedTerm, DefinedTermSet | PackageGrid, ItemListStructuredData | generic | Related API links render as linked cards and can be represented as ItemList JSON-LD. |
| RelatedPackagesBlock | Packages, Packs | SoftwareApplication, SoftwareSourceCode, Product, ItemList, Dataset, Article, BreadcrumbList | PackageGrid, ProductStructuredData, SoftwareApplicationStructuredData | generic | Related package links reuse PackageGrid and product/software schema nodes. |
| SoftwareApplicationBlock | Packages | SoftwareApplication, SoftwareSourceCode, Product, ItemList | PackageGrid, SoftwareApplicationStructuredData | generic | Software application content appears in package cards and SoftwareApplication JSON-LD. |
| SoftwareSourceCodeBlock | Packages, API_Reference | SoftwareApplication, SoftwareSourceCode, Product, ItemList, TechArticle, Code | PackageGrid, MarkdownSectionView, SoftwareSourceCodeStructuredData | generic | Source-code content is visible in package/reference sections and emitted as SoftwareSourceCode JSON-LD. |
| TechArticleBlock | Features, Packs, Comparisons | WebPage, TechArticle, DefinedTerm, BreadcrumbList, Dataset, Article, SoftwareSourceCode, ItemList, FAQPage | MarkdownSectionView, TechArticleStructuredData, ArticleStructuredData | generic | Technical article content renders through generic markdown or section copy and emits article-style JSON-LD. |
| WorkflowBlock | Workflows | HowTo, TechArticle, ItemList, BreadcrumbList | FeatureGrid, ProofMatrix, HowToStructuredData, ItemListStructuredData | generic | Workflow pages use step/question grids and proof sections plus HowTo and ItemList JSON-LD. |

## lander-react structured data components to shared structured-data types

| Structured data type | lander-react component | Shared builder | Used by SSOT Registry | SSOT sections | Notes |
| --- | --- | --- | --- | --- | --- |
| AggregateRating | AggregateRatingStructuredData | aggregateRatingNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| Article | ArticleStructuredData | articleNode | yes | Packs | Used by the SSOT Registry content pack section model. |
| BlogPosting | BlogPostingStructuredData | blogPostingNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| Book | BookStructuredData | bookNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| BreadcrumbList | BreadcrumbListStructuredData | breadcrumbListSchema | yes | Features, Proofs, Packs, FAQ_QA, Courses, Lessons, Certifications, Workflows, Comparisons, Glossary | Used by the SSOT Registry content pack section model. |
| ClaimReview | ClaimReviewStructuredData | claimReviewNode | yes | Proofs, Certifications | Used by the SSOT Registry content pack section model. |
| Course | CourseStructuredData | courseNode | yes | Courses, Certifications | Used by the SSOT Registry content pack section model. |
| CourseInstance | CourseInstanceStructuredData | courseInstanceNode | yes | Courses | Used by the SSOT Registry content pack section model. |
| Dataset | DatasetStructuredData | datasetNode | yes | Proofs, Packs | Used by the SSOT Registry content pack section model. |
| DiscussionForumPosting | DiscussionForumPostingStructuredData | discussionForumPostingNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| EmployerAggregateRating | EmployerAggregateRatingStructuredData | employerAggregateRatingNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| Event | EventStructuredData | eventNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| FAQPage | FAQPageStructuredData | faqPageSchema | yes | FAQ_QA, Comparisons | Used by the SSOT Registry content pack section model. |
| HowTo | HowToStructuredData | howToNode | yes | Lessons, Workflows | Used by the SSOT Registry content pack section model. |
| ImageObject | ImageObjectStructuredData | imageObjectSchema | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| ItemList | ItemListStructuredData | itemListNode | yes | Packages, Courses, API_Reference, Workflows, Comparisons | Used by the SSOT Registry content pack section model. |
| JobPosting | JobPostingStructuredData | jobPostingNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| LocalBusiness | LocalBusinessStructuredData | localBusinessNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| MathSolver | MathSolverStructuredData | mathSolverNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| MemberProgram | MemberProgramStructuredData | loyaltyProgramNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| MerchantReturnPolicy | MerchantReturnPolicyStructuredData | merchantReturnPolicyNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| MonetaryAmountDistribution | MonetaryAmountDistributionStructuredData | estimatedSalaryNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| Movie | MovieStructuredData | movieNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| OfferShippingDetails | OfferShippingDetailsStructuredData | offerShippingDetailsNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| Organization | OrganizationStructuredData | organizationNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| Product | ProductStructuredData | productNode | yes | Packages | Used by the SSOT Registry content pack section model. |
| ProductGroup | ProductGroupStructuredData | productGroupNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| ProfilePage | ProfilePageStructuredData | profilePageNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| QAPage | QAPageStructuredData | qaPageSchema | yes | FAQ_QA, Glossary | Used by the SSOT Registry content pack section model. |
| ReadAction | ReadActionStructuredData | readActionNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| Recipe | RecipeStructuredData | recipeNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| Review | ReviewStructuredData | reviewNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| SoftwareApplication | SoftwareApplicationStructuredData | softwareApplicationNode | yes | Packages | Used by the SSOT Registry content pack section model. |
| SoftwareSourceCode | SoftwareSourceCodeStructuredData | softwareSourceCodeNode | yes | Packages, Packs, API_Reference | Used by the SSOT Registry content pack section model. |
| SpeakableSpecification | SpeakableSpecificationStructuredData | speakableSpecificationNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| TechArticle | TechArticleStructuredData | techArticleNode | yes | Features, Lessons, API_Reference, Workflows | Used by the SSOT Registry content pack section model. |
| VacationRental | VacationRentalStructuredData | vacationRentalNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| Vehicle | VehicleStructuredData | vehicleListingNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| VideoObject | VideoObjectStructuredData | videoObjectNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| WebApplication | WebApplicationStructuredData | webApplicationNode | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
| WebPage | WebPageStructuredData | webPageSchema | yes | Features, Proofs, FAQ_QA, Comparisons | Used by the SSOT Registry content pack section model. |
| WebSite | WebSiteStructuredData | webSiteSchema | no |  | Available in lander-react shared structured-data support but not currently used by SSOT Registry content sections. |
