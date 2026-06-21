import type {
  DirectMessage,
  DmCreate,
  DmDelete,
  DmMessage,
  DmMessageCreate,
  DmMessageDelete,
  Friend,
  RelationshipDelete,
  RelationshipRequestCreate,
  ServerRailLayout,
  StoreCatalog,
  StoreItemDetail,
} from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

async function readError(response: Response) {
  try {
    const payload = (await response.json()) as { detail?: string }
    if (payload.detail) {
      return new Error(payload.detail)
    }
  } catch {
    // Fall through to the generic status message.
  }
  if (response.status >= 500) {
    return new Error('서버 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.')
  }
  if (response.status === 401) {
    return new Error('로그인이 필요합니다.')
  }
  if (response.status === 403) {
    return new Error('이 작업을 수행할 권한이 없습니다.')
  }
  if (response.status === 404) {
    return new Error('요청한 항목을 찾을 수 없습니다.')
  }
  return new Error(`요청을 완료하지 못했습니다. (${response.status})`)
}

export async function apiGet<T>(path: string, token?: string | null): Promise<T> {
  const headers = new Headers()
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  const response = await fetch(`${API_BASE_URL}${path}`, { headers })
  if (!response.ok) {
    throw await readError(response)
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
    throw await readError(response)
  }
  return response.json() as Promise<TResponse>
}

export async function apiPatch<TResponse, TPayload>(
  path: string,
  payload: TPayload,
  token?: string | null,
): Promise<TResponse> {
  const headers = new Headers({ 'Content-Type': 'application/json' })
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw await readError(response)
  }
  return response.json() as Promise<TResponse>
}

export async function apiPut<TResponse, TPayload>(
  path: string,
  payload: TPayload,
  token?: string | null,
): Promise<TResponse> {
  const headers = new Headers({ 'Content-Type': 'application/json' })
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'PUT',
    headers,
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw await readError(response)
  }
  return response.json() as Promise<TResponse>
}

export async function apiDelete<TResponse>(path: string, token?: string | null): Promise<TResponse> {
  const headers = new Headers()
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'DELETE',
    headers,
  })
  if (!response.ok) {
    throw await readError(response)
  }
  return response.json() as Promise<TResponse>
}

export function fetchStoreCatalog(token?: string | null): Promise<StoreCatalog> {
  return apiGet<StoreCatalog>('/api/store/catalog', token)
}

export function fetchStoreItemDetail(
  itemId: number,
  token?: string | null,
): Promise<StoreItemDetail> {
  return apiGet<StoreItemDetail>(`/api/store/items/${itemId}`, token)
}

export function fetchRelationships(token?: string | null): Promise<Friend[]> {
  return apiGet<Friend[]>('/api/users/me/relationships', token)
}

export function createFriendRequest(
  payload: RelationshipRequestCreate,
  token?: string | null,
): Promise<Friend> {
  return apiPost<Friend, RelationshipRequestCreate>(
    '/api/users/me/relationships/requests',
    payload,
    token,
  )
}

export function acceptFriendRequest(userId: number, token?: string | null): Promise<Friend> {
  return apiPost<Friend, Record<string, never>>(
    `/api/users/me/relationships/${userId}/accept`,
    {},
    token,
  )
}

export function rejectFriendRequest(
  userId: number,
  token?: string | null,
): Promise<RelationshipDelete> {
  return apiPost<RelationshipDelete, Record<string, never>>(
    `/api/users/me/relationships/${userId}/reject`,
    {},
    token,
  )
}

export function cancelFriendRequest(
  userId: number,
  token?: string | null,
): Promise<RelationshipDelete> {
  return apiPost<RelationshipDelete, Record<string, never>>(
    `/api/users/me/relationships/${userId}/cancel`,
    {},
    token,
  )
}

export function removeFriend(userId: number, token?: string | null): Promise<RelationshipDelete> {
  return apiDelete<RelationshipDelete>(`/api/users/me/relationships/${userId}`, token)
}

export function blockFriend(userId: number, token?: string | null): Promise<Friend> {
  return apiPost<Friend, Record<string, never>>(
    `/api/users/me/relationships/${userId}/block`,
    {},
    token,
  )
}

export function unblockFriend(userId: number, token?: string | null): Promise<RelationshipDelete> {
  return apiDelete<RelationshipDelete>(`/api/users/me/relationships/${userId}/block`, token)
}

export function fetchServerRailLayout(token?: string | null): Promise<ServerRailLayout> {
  return apiGet<ServerRailLayout>('/api/users/me/server-rail', token)
}

export function updateServerRailLayout(
  payload: ServerRailLayout,
  token?: string | null,
): Promise<ServerRailLayout> {
  return apiPut<ServerRailLayout, ServerRailLayout>('/api/users/me/server-rail', payload, token)
}

export function fetchDirectMessages(token?: string | null): Promise<DirectMessage[]> {
  return apiGet<DirectMessage[]>('/api/dms', token)
}

export function createDirectMessage(
  payload: DmCreate,
  token?: string | null,
): Promise<DirectMessage> {
  return apiPost<DirectMessage, DmCreate>('/api/dms', payload, token)
}

export function createDirectMessageMessage(
  dmId: number,
  payload: DmMessageCreate,
  token?: string | null,
): Promise<DmMessage> {
  return apiPost<DmMessage, DmMessageCreate>(`/api/dms/${dmId}/messages`, payload, token)
}

export function deleteDirectMessageMessage(
  dmId: number,
  messageId: number,
  token?: string | null,
): Promise<DmMessageDelete> {
  return apiDelete<DmMessageDelete>(`/api/dms/${dmId}/messages/${messageId}`, token)
}

export function deleteDirectMessage(
  dmId: number,
  token?: string | null,
): Promise<DmDelete> {
  return apiDelete<DmDelete>(`/api/dms/${dmId}`, token)
}
