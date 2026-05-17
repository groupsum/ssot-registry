import React from "react";
import { createRoot } from "react-dom/client";
import "@mdwrk/lander-theme/styles/default.css";
import { App } from "./App";
import "./styles.css";

const rootElement = document.getElementById("root")!;
rootElement.classList.remove("app-boot-shell");
rootElement.removeAttribute("aria-busy");

createRoot(rootElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
