import { LanderPage } from "@mdwrk/lander-react";
import { ssotRegistrySite } from "@ssot-registry/site-content-pack";

const normalizedCanonicalRoot = ssotRegistrySite.product.canonicalUrl.replace(/\/+$/, "");
const normalizePath = (value: string) => {
  const path = value === "" ? "/" : value.split(/[?#]/)[0] ?? "/";
  if (path === "/" || path === "") return "/";
  return `/${path.replace(/^\/+|\/+$/g, "")}/`;
};

function compilePage(page: (typeof ssotRegistrySite.pages)[number]) {
  const path = normalizePath(page.slug);
  return {
    ...page,
    path,
    canonicalUrl: `${normalizedCanonicalRoot}${path}`,
    breadcrumbs: breadcrumbItems(page.slug),
    internalLinks: [],
    wordCount: wordCount([page.title, page.description, page.intro, JSON.stringify(page.sections)].join(" ")),
    componentIntents: [],
    schemaIntents: [],
  };
}

function currentPage() {
  const browserPath = typeof window === "undefined" ? "/" : window.location.pathname;
  const path = normalizePath(browserPath);
  const page = ssotRegistrySite.pages.find((candidate) => normalizePath(candidate.slug) === path) ?? ssotRegistrySite.pages[0];
  if (!page) {
    throw new Error("SSOT Registry content pack did not define a routable page.");
  }
  return compilePage(page);
}

function siteForPage(page: ReturnType<typeof compilePage>) {
  return {
    ...ssotRegistrySite,
    pages: [page],
    pageByPath: new Map([[page.path, page]]),
    diagnostics: [],
  };
}

function breadcrumbItems(slug: string) {
  const segments = normalizePath(slug).split("/").filter(Boolean);
  const items = [{ label: ssotRegistrySite.product.name, href: "/" }];
  let href = "";
  for (const segment of segments) {
    href = `${href}/${segment}`;
    items.push({ label: titleCase(segment), href: `${href}/` });
  }
  return items;
}

function titleCase(value: string) {
  return value.replace(/-/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

function wordCount(value: string) {
  return value.trim().split(/\s+/).filter(Boolean).length;
}

export function App() {
  const page = currentPage();
  const compiledSite = siteForPage(page);
  return (
    <div
      className="site-shell"
      data-page-path={page.path}
      data-lander-theme={ssotRegistrySite.theme?.mode === "dark" ? "lander-dark" : "lander-light"}
    >
      <header className="site-header">
        <div className="site-nav">
          <a className="site-brand" href="/" aria-label="SSOT Registry home">
            <span className="site-brand-mark" aria-hidden="true">SR</span>
            <span className="site-brand-text">
              <span className="site-brand-name">{ssotRegistrySite.product.name}</span>
              <span className="site-brand-tagline">{ssotRegistrySite.product.tagline}</span>
            </span>
          </a>
          <nav className="site-nav-links" aria-label="Primary navigation">
            {ssotRegistrySite.nav?.primary.map((item) => (
              <a key={item.href} href={item.href}>{item.label}</a>
            ))}
          </nav>
          {ssotRegistrySite.nav?.cta ? (
            <a className="site-nav-cta" href={ssotRegistrySite.nav.cta.href}>
              {ssotRegistrySite.nav.cta.label}
            </a>
          ) : null}
        </div>
      </header>
      <main id="main-content" className="site-main">
        <LanderPage site={compiledSite as any} page={page as any} />
      </main>
      <footer className="site-footer">
        <p>{ssotRegistrySite.footer?.note}</p>
        <nav aria-label="Footer links">
          {ssotRegistrySite.footer?.links?.map((item) => (
            <a key={item.href} href={item.href}>{item.label}</a>
          ))}
        </nav>
      </footer>
    </div>
  );
}
