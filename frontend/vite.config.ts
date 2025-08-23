import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from "path";
import fs from "fs";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  return {
    plugins: [
      react(),
      {
        name: "manifest-replace-google-oauth-client-id",
        buildEnd() {
          const manifest = fs
            .readFileSync("manifest.template.json", "utf8")
            .replace("__GOOGLE_OAUTH_CLIENT_ID_BROWSER_EXTENSION__", env.VITE_GOOGLE_OAUTH_CLIENT_ID || "");
          fs.writeFileSync("public/manifest.json", manifest);
        },
      },
    ],
    build: {
      rollupOptions: {
        input: {
          // web: resolve(__dirname, "src/web/index.html"),                          // normal website
          popup: resolve(__dirname, "src/browser_extension/popup.html"),          // extension popup
          background: resolve(__dirname, "src/browser_extension/background.ts"),
        },
        output: {
          entryFileNames: "assets/[name].js",
          chunkFileNames: "assets/[name].js",
          assetFileNames: "assets/[name].[ext]"
        }
      },
      outDir: "dist",
      emptyOutDir: true
    },
    server: {
      port: 3000,
    },
  }
});
