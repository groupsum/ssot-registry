import React from "react";

export function Section({
  title,
  children,
  className = "",
  collapsible = false,
  defaultOpen = true,
}: {
  title?: string;
  children: React.ReactNode;
  className?: string;
  collapsible?: boolean;
  defaultOpen?: boolean;
}): React.ReactElement {
  const sectionClassName = `ssot-section ${className}`.trim();
  if (collapsible) {
    return (
      <details className={`${sectionClassName} ssot-accordion-section`} open={defaultOpen}>
        <summary className="ssot-accordion-summary">
          {title ? <h2 className="ssot-section-title">{title}</h2> : null}
          <span className="ssot-accordion-indicator" aria-hidden="true" />
        </summary>
        <div className="ssot-accordion-body">{children}</div>
      </details>
    );
  }

  return (
    <section className={sectionClassName}>
      {title ? <h2 className="ssot-section-title">{title}</h2> : null}
      {children}
    </section>
  );
}
