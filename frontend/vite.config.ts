import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

/**
 * Vite Configuration
 *
 * What is this file?
 * Vite uses this to configure the dev server, build process, and plugins.
 *
 * Key concepts:
 * - server.proxy: Forwards API calls to the FastAPI backend.
 *   When the frontend calls fetch('/api/graph'), Vite intercepts it
 *   and forwards it to http://localhost:8000/api/graph.
 *   This avoids CORS issues in development.
 *
 * Interview Q: "What is a reverse proxy and why use it in development?"
 * Answer: A reverse proxy forwards requests from one server to another.
 * In dev, the frontend runs on port 5173 and the backend on port 8000.
 * The proxy makes them appear as the same origin to the browser.
 */
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: {
      '@': '/src',
    },
  },
})
