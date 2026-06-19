import { defineStore } from 'pinia'
import { ref } from 'vue'

import { browserStorage } from '../services/browserApi'

export type AppDestination = 'friends' | 'dm' | 'server_channel' | 'voice_channel' | 'settings'
export type RestorableDestination = Exclude<AppDestination, 'settings'>

export interface PersistedWorkspaceLocation {
  userId: number
  destination: RestorableDestination
  activeDmId: number | null
  activeGuildId: number | null
  activeChannelId: number | null
}

const WORKSPACE_LOCATION_STORAGE_KEY = 'discord-clone-workspace-location'
const RESTORABLE_DESTINATIONS: RestorableDestination[] = [
  'friends',
  'dm',
  'server_channel',
  'voice_channel',
]

function isRestorableDestination(value: unknown): value is RestorableDestination {
  return typeof value === 'string' && RESTORABLE_DESTINATIONS.includes(value as RestorableDestination)
}

function nullableNumber(value: unknown): number | null {
  return typeof value === 'number' && Number.isSafeInteger(value) ? value : null
}

function parseWorkspaceLocation(rawLocation: string | null): PersistedWorkspaceLocation | null {
  if (!rawLocation) return null

  try {
    const parsed = JSON.parse(rawLocation) as Record<string, unknown>
    if (!Number.isSafeInteger(parsed.userId) || !isRestorableDestination(parsed.destination)) {
      return null
    }
    return {
      userId: parsed.userId as number,
      destination: parsed.destination,
      activeDmId: nullableNumber(parsed.activeDmId),
      activeGuildId: nullableNumber(parsed.activeGuildId),
      activeChannelId: nullableNumber(parsed.activeChannelId),
    }
  } catch {
    return null
  }
}

export const useNavigationStore = defineStore('navigation', () => {
  const destination = ref<AppDestination>('friends')
  const activeDmId = ref<number | null>(null)
  const settingsReturnDestination = ref<AppDestination>('friends')
  const settingsReturnDmId = ref<number | null>(null)

  function openFriends() {
    destination.value = 'friends'
    activeDmId.value = null
  }

  function openDm(dmId: number) {
    destination.value = 'dm'
    activeDmId.value = dmId
  }

  function openServerChannel() {
    destination.value = 'server_channel'
    activeDmId.value = null
  }

  function openVoiceChannel() {
    destination.value = 'voice_channel'
    activeDmId.value = null
  }

  function openSettings() {
    if (destination.value !== 'settings') {
      settingsReturnDestination.value = destination.value
      settingsReturnDmId.value = activeDmId.value
    }
    destination.value = 'settings'
  }

  function closeSettings() {
    destination.value = settingsReturnDestination.value
    activeDmId.value = settingsReturnDmId.value
  }

  function resetNavigation() {
    destination.value = 'friends'
    activeDmId.value = null
    settingsReturnDestination.value = 'friends'
    settingsReturnDmId.value = null
  }

  function snapshotWorkspaceLocation(
    userId: number,
    activeGuildId: number | null,
    activeChannelId: number | null,
  ): PersistedWorkspaceLocation {
    const targetDestination = destination.value === 'settings'
      ? settingsReturnDestination.value
      : destination.value
    const targetDmId = destination.value === 'settings'
      ? settingsReturnDmId.value
      : activeDmId.value

    return {
      userId,
      destination: targetDestination === 'settings' ? 'friends' : targetDestination,
      activeDmId: targetDestination === 'dm' ? targetDmId : null,
      activeGuildId,
      activeChannelId,
    }
  }

  function persistWorkspaceLocation(
    userId: number,
    activeGuildId: number | null,
    activeChannelId: number | null,
  ) {
    const location = snapshotWorkspaceLocation(userId, activeGuildId, activeChannelId)
    browserStorage.setItem(WORKSPACE_LOCATION_STORAGE_KEY, JSON.stringify(location))
  }

  function readPersistedWorkspaceLocation(userId: number) {
    const location = parseWorkspaceLocation(browserStorage.getItem(WORKSPACE_LOCATION_STORAGE_KEY))
    if (!location || location.userId !== userId) return null
    return location
  }

  function clearPersistedWorkspaceLocation() {
    browserStorage.removeItem(WORKSPACE_LOCATION_STORAGE_KEY)
  }

  return {
    destination,
    activeDmId,
    openFriends,
    openDm,
    openServerChannel,
    openVoiceChannel,
    openSettings,
    closeSettings,
    resetNavigation,
    persistWorkspaceLocation,
    readPersistedWorkspaceLocation,
    clearPersistedWorkspaceLocation,
  }
})
