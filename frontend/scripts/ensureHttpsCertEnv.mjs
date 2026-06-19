import { existsSync } from 'node:fs'

const keyFile = process.env.VITE_HTTPS_KEY_FILE
const certFile = process.env.VITE_HTTPS_CERT_FILE

const missing = []
if (!keyFile) missing.push('VITE_HTTPS_KEY_FILE')
if (!certFile) missing.push('VITE_HTTPS_CERT_FILE')

if (missing.length > 0) {
  console.error(`Missing ${missing.join(' and ')}.`)
  console.error('Set both variables to local development certificate files before running HTTPS LAN.')
  process.exit(1)
}

const missingFiles = []
if (!existsSync(keyFile)) missingFiles.push(keyFile)
if (!existsSync(certFile)) missingFiles.push(certFile)

if (missingFiles.length > 0) {
  console.error(`HTTPS certificate file not found: ${missingFiles.join(', ')}`)
  process.exit(1)
}
