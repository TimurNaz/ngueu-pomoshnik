import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
	plugins: [react()],
	root: '.',
	build: {
		outDir: 'dist',
		sourcemap: true,
	},
	server: {
		port: 3000,
		strictPort: true,
		allowedHosts: true, // чтобы открывать приложение через ngrok из Telegram
	},
	preview: {
		port: 3000,
	},
})
