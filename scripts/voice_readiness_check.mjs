const REST_BASE = process.env.REST_BASE ?? 'http://127.0.0.1:8000'

const response = await fetch(`${REST_BASE}/api/meta/voice/readiness`)
if (!response.ok) {
  throw new Error(`voice readiness check failed with ${response.status}`)
}

const readiness = await response.json()
const result = {
  endpoint: `${REST_BASE}/api/meta/voice/readiness`,
  ice_server_count: Number(readiness.ice_server_count ?? 0),
  stun_configured: Boolean(readiness.stun_configured),
  turn_configured: Boolean(readiness.turn_configured),
}

console.log(JSON.stringify(result, null, 2))

if (!result.turn_configured) {
  console.log('TURN is not configured. Do not mark TURN/NAT internet voice complete.')
}
