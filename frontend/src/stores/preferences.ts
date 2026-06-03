import { defineStore } from 'pinia'
import { ref } from 'vue'

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
    const rawPreferences = localStorage.getItem(PREFERENCES_STORAGE_KEY)
    if (!rawPreferences) return

    try {
      const preferences = JSON.parse(rawPreferences) as PersistedPreferences
      if (isAppLanguage(preferences.language)) {
        language.value = preferences.language
      }
    } catch {
      localStorage.removeItem(PREFERENCES_STORAGE_KEY)
    }
  }

  function persistPreferences() {
    const preferences: PersistedPreferences = {
      language: language.value,
    }
    localStorage.setItem(PREFERENCES_STORAGE_KEY, JSON.stringify(preferences))
  }

  function setLanguage(nextLanguage: AppLanguage) {
    language.value = nextLanguage
    persistPreferences()
  }

  return { language, restorePreferences, setLanguage }
})
