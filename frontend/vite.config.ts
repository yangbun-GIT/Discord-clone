import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { readFileSync } from 'node:fs'

const backendProxyTarget = process.env.VITE_BACKEND_PROXY_TARGET ?? 'http://127.0.0.1:8000'
const gatewayProxyTarget = backendProxyTarget.replace(/^http/, 'ws')
const httpsPfxFile = process.env.VITE_HTTPS_PFX_FILE
const httpsPfxPassphrase = process.env.VITE_HTTPS_PFX_PASSPHRASE
const httpsKeyFile = process.env.VITE_HTTPS_KEY_FILE
const httpsCertFile = process.env.VITE_HTTPS_CERT_FILE
const https =
  httpsPfxFile
    ? {
        pfx: readFileSync(httpsPfxFile),
        passphrase: httpsPfxPassphrase,
      }
    : httpsKeyFile && httpsCertFile
    ? {
        key: readFileSync(httpsKeyFile),
        cert: readFileSync(httpsCertFile),
      }
    : undefined

export default defineConfig({
  plugins: [vue()],
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
