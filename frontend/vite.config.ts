import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { noiseSuppressionAudioWorkletVitePlugin } from '@workadventure/noise-suppression/vite'
import { readFileSync } from 'node:fs'

const backendProxyTarget = process.env.VITE_BACKEND_PROXY_TARGET ?? 'http://127.0.0.1:8000'
const gatewayProxyTarget = backendProxyTarget.replace(/^http/, 'ws')
const httpsKeyFile = process.env.VITE_HTTPS_KEY_FILE
const httpsCertFile = process.env.VITE_HTTPS_CERT_FILE
const https =
  httpsKeyFile && httpsCertFile
    ? {
        key: readFileSync(httpsKeyFile),
        cert: readFileSync(httpsCertFile),
      }
    : undefined

export default defineConfig({
  plugins: [vue(), noiseSuppressionAudioWorkletVitePlugin()],
  server: {
    port: 5173,
    https,
    proxy: {
      '/api': backendProxyTarget,
      '/gateway': {
        target: gatewayProxyTarget,
        ws: true,
      },
    },
  },
})
