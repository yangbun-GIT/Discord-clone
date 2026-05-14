import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const backendProxyTarget = process.env.VITE_BACKEND_PROXY_TARGET ?? 'http://127.0.0.1:8000'
const gatewayProxyTarget = backendProxyTarget.replace(/^http/, 'ws')

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': backendProxyTarget,
      '/gateway': {
        target: gatewayProxyTarget,
        ws: true,
      },
    },
  },
})
