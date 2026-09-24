import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // In development, forward API calls to the Django backend.
    // In Docker/Kubernetes, Nginx does this job (see nginx.conf).
    proxy: {
      '/students': 'http://localhost:8090',
      '/health': 'http://localhost:8090',
    },
  },
})
