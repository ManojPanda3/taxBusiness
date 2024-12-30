import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // Replace with your actual backend server
        changeOrigin: true,
        pathRewrite: {
          '^/api': '' // Remove the '/api' prefix from the request URL
        }
      }
    }
  }
})
