import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from "path";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: {
        popup: resolve(__dirname, "browser_extension/popup.html"),          // extension popup
        background: resolve(__dirname, "browser_extension/background.ts"),  // background worker
      },
    },
    outDir: "dist",
    emptyOutDir: true
  },

  server: {
    port: 3000,
  },
})
