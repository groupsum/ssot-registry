import { LanderPage } from "@mdwrk/lander-react";
import { ssotRegistrySite } from "@ssot-registry/site-content-pack";

const normalizedCanonicalRoot = ssotRegistrySite.product.canonicalUrl.replace(/\/+$/, "");
const normalizePath = (value: string) => {
  const path = value === "" ? "/" : value.split(/[?#]/)[0] ?? "/";
  if (path === "/" || path === "") return "/";
  return `/${path.replace(/^\/+|\/+$/g, "")}/`;
};

const compiledPages = ssotRegistrySite.pages.map((page) => {
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
});

const compiledSite = {
  ...ssotRegistrySite,
  pages: compiledPages,
  pageByPath: new Map(compiledPages.map((page) => [page.path, page])),
  diagnostics: [],
};

function currentPage() {
  const browserPath = typeof window === "undefined" ? "/" : window.location.pathname;
  const path = normalizePath(browserPath);
  const page = compiledSite.pageByPath.get(path) ?? compiledSite.pageByPath.get("/");
  if (!page) {
    throw new Error("SSOT Registry content pack did not define a routable page.");
  }
  return page;
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
  return (
    <div
      className="site-shell"
      data-page-path={page.path}
      data-lander-theme={ssotRegistrySite.theme?.mode === "dark" ? "lander-dark" : "lander-light"}
    >
      <header className="site-header">
        <div className="site-nav">
          <a className="site-brand" href="/" aria-label="SSOT Registry home">
            <span className="site-brand-mark">
              <img src="/favicon-32.png" alt="" width="24" height="24" />
            </span>
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
      <LanderPage site={compiledSite as any} page={page as any} />
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
