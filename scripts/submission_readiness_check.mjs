const DEFAULT_ORIGINS = [
  'http://127.0.0.1:5173',
  'http://localhost:5173',
  'https://localhost:5173',
  'https://127.0.0.1:5173',
]

if (process.env.SUBMISSION_IGNORE_TLS_ERRORS !== '0') {
  process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0'
}

const configuredOrigins = process.env.SUBMISSION_ORIGIN
  ? [process.env.SUBMISSION_ORIGIN]
  : DEFAULT_ORIGINS

const toWsUrl = (origin, pathname) => {
  const url = new URL(pathname, origin)
  url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
  return url.toString()
}

async function fetchWithTimeout(url, options = {}) {
  return await fetch(url, {
    ...options,
    signal: AbortSignal.timeout(5000),
  })
}

async function fetchJson(origin, pathname) {
  const response = await fetchWithTimeout(new URL(pathname, origin))
  if (!response.ok) {
    throw new Error(`${pathname} returned HTTP ${response.status}`)
  }
  return await response.json()
}

async function checkFrontend(origin) {
  const response = await fetchWithTimeout(origin)
  if (!response.ok) {
    throw new Error(`frontend returned HTTP ${response.status}`)
  }
  const body = await response.text()
  if (!body.includes('<html') && !body.includes('<div id="app"')) {
    throw new Error('frontend response did not look like the app HTML')
  }
}

async function waitForGatewayHello(origin) {
  const socket = new WebSocket(toWsUrl(origin, '/gateway'))

  return await new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      socket.close()
      reject(new Error('/gateway did not send HELLO before timeout'))
    }, 5000)

    socket.addEventListener('message', (event) => {
      try {
        const payload = JSON.parse(String(event.data))
        if (payload.op === 10) {
          clearTimeout(timeout)
          socket.close()
          resolve(true)
        }
      } catch {
        clearTimeout(timeout)
        socket.close()
        reject(new Error('/gateway sent a non-JSON message before HELLO'))
      }
    })

    socket.addEventListener('error', () => {
      clearTimeout(timeout)
      reject(new Error('/gateway WebSocket connection failed'))
    })
  })
}

async function checkOrigin(rawOrigin) {
  const origin = new URL(rawOrigin)
  await checkFrontend(origin)
  const health = await fetchJson(origin, '/api/health')
  const readiness = await fetchJson(origin, '/api/meta/voice/readiness')
  await waitForGatewayHello(origin)

  return {
    origin: origin.toString(),
    secure_origin: origin.protocol === 'https:',
    frontend: true,
    health_status: health.status ?? 'unknown',
    database_configured: Boolean(health.database?.configured),
    redis_configured: Boolean(health.redis?.configured),
    ice_server_count: Number(readiness.ice_server_count ?? 0),
    stun_configured: Boolean(readiness.stun_configured),
    turn_configured: Boolean(readiness.turn_configured),
    gateway_hello: true,
  }
}

const failures = []
let result = null

for (const origin of configuredOrigins) {
  try {
    result = await checkOrigin(origin)
    break
  } catch (error) {
    failures.push({
      origin,
      error: error instanceof Error ? error.message : String(error),
    })
  }
}

if (!result) {
  console.error(JSON.stringify({ status: 'failed', failures }, null, 2))
  throw new Error('No local submission origin passed readiness checks')
}

console.log(JSON.stringify(result, null, 2))

if (!result.database_configured) {
  throw new Error('Local submission check expects Docker PostgreSQL to be configured')
}

if (!result.turn_configured) {
  console.log('TURN is not configured. This is acceptable for local submission but not for external TURN/NAT voice completion.')
}
