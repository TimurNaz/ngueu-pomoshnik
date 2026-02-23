import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
	plugins: [react()],
	server: {
		port: 3000,
		host: true,
		allowedHosts: 'all', // ← добавь эту строку
	},
	preview: {
		port: 3000,
	},
	build: {
		outDir: 'dist',
		sourcemap: false,
	},
})
