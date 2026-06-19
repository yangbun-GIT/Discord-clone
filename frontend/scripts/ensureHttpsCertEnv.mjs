import { existsSync } from 'node:fs'

const pfxFile = process.env.VITE_HTTPS_PFX_FILE
const keyFile = process.env.VITE_HTTPS_KEY_FILE
const certFile = process.env.VITE_HTTPS_CERT_FILE

if (pfxFile) {
  if (!existsSync(pfxFile)) {
    console.error(`HTTPS PFX certificate file not found: ${pfxFile}`)
    process.exit(1)
  }
  process.exit(0)
}

const missing = []
if (!keyFile) missing.push('VITE_HTTPS_KEY_FILE')
if (!certFile) missing.push('VITE_HTTPS_CERT_FILE')

if (missing.length > 0) {
  console.error(`Missing ${missing.join(' and ')}.`)
  console.error(
    'Set VITE_HTTPS_PFX_FILE or both VITE_HTTPS_KEY_FILE and VITE_HTTPS_CERT_FILE before running HTTPS LAN.',
  )
  process.exit(1)
}

const missingFiles = []
if (!existsSync(keyFile)) missingFiles.push(keyFile)
if (!existsSync(certFile)) missingFiles.push(certFile)

if (missingFiles.length > 0) {
  console.error(`HTTPS certificate file not found: ${missingFiles.join(', ')}`)
  process.exit(1)
}
