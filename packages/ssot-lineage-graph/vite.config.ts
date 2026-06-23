import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";

export default defineConfig(({ mode }) => {
  const standalone = mode === "standalone";
  return {
    plugins: [react(), tailwindcss()],
    build: standalone
      ? {
          outDir: "dist/standalone",
          emptyOutDir: true,
          cssCodeSplit: false,
          rollupOptions: {
            input: "src/standalone.tsx",
            output: {
              entryFileNames: "ssot-lineage-graph.js",
              assetFileNames: "ssot-lineage-graph.[ext]",
            },
          },
        }
      : {
          lib: {
            entry: "src/index.ts",
            name: "SsotLineageGraph",
            fileName: "lineage-graph",
            formats: ["es", "cjs"],
          },
          rollupOptions: {
            external: ["react", "react-dom", "react-dom/client"],
            output: {
              globals: {
                react: "React",
                "react-dom": "ReactDOM",
                "react-dom/client": "ReactDOM",
              },
            },
          },
        },
  };
});
