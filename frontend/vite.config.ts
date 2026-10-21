import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Proxy API calls to the FastAPI backend so the browser only talks to one origin.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/ws': { target: 'ws://localhost:8000', ws: true },
    },
  },
})
