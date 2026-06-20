import { defineStore } from 'pinia'
import { ref } from 'vue'

import { browserStorage } from '../services/browserApi'

export type AppLanguage = 'ko' | 'en'

const PREFERENCES_STORAGE_KEY = 'discord-clone-preferences'

type PersistedPreferences = {
  language?: AppLanguage
  mutedDmIds?: number[]
}

function isAppLanguage(value: unknown): value is AppLanguage {
  return value === 'ko' || value === 'en'
}

export const usePreferencesStore = defineStore('preferences', () => {
  const language = ref<AppLanguage>('ko')
  const mutedDmIds = ref<number[]>([])

  function restorePreferences() {
    const rawPreferences = browserStorage.getItem(PREFERENCES_STORAGE_KEY)
    if (!rawPreferences) return

    try {
      const preferences = JSON.parse(rawPreferences) as PersistedPreferences
      if (isAppLanguage(preferences.language)) {
        language.value = preferences.language
      }
      if (Array.isArray(preferences.mutedDmIds)) {
        mutedDmIds.value = preferences.mutedDmIds.filter((id): id is number => Number.isSafeInteger(id))
      }
    } catch {
      browserStorage.removeItem(PREFERENCES_STORAGE_KEY)
    }
  }

  function persistPreferences() {
    const preferences: PersistedPreferences = {
      language: language.value,
      mutedDmIds: mutedDmIds.value,
    }
    browserStorage.setItem(PREFERENCES_STORAGE_KEY, JSON.stringify(preferences))
  }

  function setLanguage(nextLanguage: AppLanguage) {
    language.value = nextLanguage
    persistPreferences()
  }

  function isDmMuted(dmId: number | null) {
    return dmId !== null && mutedDmIds.value.includes(dmId)
  }

  function setDmMuted(dmId: number, muted: boolean) {
    mutedDmIds.value = muted
      ? Array.from(new Set([...mutedDmIds.value, dmId]))
      : mutedDmIds.value.filter((id) => id !== dmId)
    persistPreferences()
  }

  function toggleDmMuted(dmId: number) {
    setDmMuted(dmId, !isDmMuted(dmId))
  }

  return {
    language,
    mutedDmIds,
    restorePreferences,
    setLanguage,
    isDmMuted,
    setDmMuted,
    toggleDmMuted,
  }
})
