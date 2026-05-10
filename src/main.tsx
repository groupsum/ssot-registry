import React from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

function App() {
  return (
    <main className="page">
      <section className="panel" aria-labelledby="headline">
        <p className="eyebrow">SSOT Registry</p>
        <h1 id="headline">Hello, world.</h1>
        <p className="copy">
          A lightweight TypeScript React landing page for the SSOT Registry
          deployment target.
        </p>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
