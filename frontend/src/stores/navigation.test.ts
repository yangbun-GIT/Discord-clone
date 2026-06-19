import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import { useNavigationStore } from './navigation'

function createMemoryStorage() {
  const store = new Map<string, string>()
  return {
    getItem: vi.fn((key: string) => store.get(key) ?? null),
    setItem: vi.fn((key: string, value: string) => {
      store.set(key, value)
    }),
    removeItem: vi.fn((key: string) => {
      store.delete(key)
    }),
    clear: () => store.clear(),
  }
}

const storage = createMemoryStorage()

describe('navigation workspace persistence', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    storage.clear()
    vi.stubGlobal('localStorage', storage)
  })

  it('persists and restores the active server channel for the same user', () => {
    const navigation = useNavigationStore()
    navigation.openServerChannel()

    navigation.persistWorkspaceLocation(101, 201, 301)

    expect(navigation.readPersistedWorkspaceLocation(101)).toEqual({
      userId: 101,
      destination: 'server_channel',
      activeDmId: null,
      activeGuildId: 201,
      activeChannelId: 301,
    })
  })

  it('persists the settings return target instead of settings itself', () => {
    const navigation = useNavigationStore()
    navigation.openDm(401)
    navigation.openSettings()

    navigation.persistWorkspaceLocation(101, null, null)

    expect(navigation.readPersistedWorkspaceLocation(101)).toEqual({
      userId: 101,
      destination: 'dm',
      activeDmId: 401,
      activeGuildId: null,
      activeChannelId: null,
    })
  })

  it('does not restore a location saved by another user', () => {
    const navigation = useNavigationStore()
    navigation.openVoiceChannel()
    navigation.persistWorkspaceLocation(101, 201, 302)

    expect(navigation.readPersistedWorkspaceLocation(102)).toBeNull()
  })

  it('clears the persisted workspace location on logout cleanup', () => {
    const navigation = useNavigationStore()
    navigation.openServerChannel()
    navigation.persistWorkspaceLocation(101, 201, 301)

    navigation.clearPersistedWorkspaceLocation()

    expect(navigation.readPersistedWorkspaceLocation(101)).toBeNull()
  })
})
