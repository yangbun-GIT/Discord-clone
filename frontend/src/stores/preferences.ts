import { defineStore } from 'pinia'
import { ref } from 'vue'

import { browserStorage } from '../services/browserApi'

export type AppLanguage = 'ko' | 'en'

const PREFERENCES_STORAGE_KEY = 'discord-clone-preferences'

type PersistedPreferences = {
  language?: AppLanguage
}

function isAppLanguage(value: unknown): value is AppLanguage {
  return value === 'ko' || value === 'en'
}

export const usePreferencesStore = defineStore('preferences', () => {
  const language = ref<AppLanguage>('ko')

  function restorePreferences() {
    const rawPreferences = browserStorage.getItem(PREFERENCES_STORAGE_KEY)
    if (!rawPreferences) return

    try {
      const preferences = JSON.parse(rawPreferences) as PersistedPreferences
      if (isAppLanguage(preferences.language)) {
        language.value = preferences.language
      }
    } catch {
      browserStorage.removeItem(PREFERENCES_STORAGE_KEY)
    }
  }

  function persistPreferences() {
    const preferences: PersistedPreferences = {
      language: language.value,
    }
    browserStorage.setItem(PREFERENCES_STORAGE_KEY, JSON.stringify(preferences))
  }

  function setLanguage(nextLanguage: AppLanguage) {
    language.value = nextLanguage
    persistPreferences()
  }

  return { language, restorePreferences, setLanguage }
})
