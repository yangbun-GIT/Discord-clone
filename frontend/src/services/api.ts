const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

async function readError(response: Response, method: string, path: string) {
  try {
    const payload = (await response.json()) as { detail?: string }
    if (payload.detail) {
      return new Error(payload.detail)
    }
  } catch {
    // Fall through to the generic status message.
  }
  return new Error(`${method} ${path} failed with ${response.status}`)
}

export async function apiGet<T>(path: string, token?: string | null): Promise<T> {
  const headers = new Headers()
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  const response = await fetch(`${API_BASE_URL}${path}`, { headers })
  if (!response.ok) {
    throw await readError(response, 'GET', path)
  }
  return response.json() as Promise<T>
}

export async function apiPost<TResponse, TPayload>(
  path: string,
  payload: TPayload,
  token?: string | null,
): Promise<TResponse> {
  const headers = new Headers({ 'Content-Type': 'application/json' })
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw await readError(response, 'POST', path)
  }
  return response.json() as Promise<TResponse>
}
