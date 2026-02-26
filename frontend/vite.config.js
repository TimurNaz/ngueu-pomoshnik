import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true, // Позволяет Vite слушать внешние подключения
    allowedHosts: true, // Разрешает любые хосты (ngrok, localtunnel)
    proxy: {
      // Все запросы, начинающиеся с /api, будут уходить на бэкенд (порт 8000)
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
