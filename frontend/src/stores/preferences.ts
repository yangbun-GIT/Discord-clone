import { defineStore } from 'pinia'
import { ref } from 'vue'

import { browserStorage } from '../services/browserApi'

export type AppLanguage = 'ko' | 'en'
export type AppTheme = 'dark' | 'darker'
export type AppDensity = 'comfortable' | 'compact'
export type NotificationMode = 'all' | 'mentions' | 'none'
export type FriendRequestPolicy = 'everyone' | 'friends_of_friends' | 'none'
export type TimeFormat = 'auto' | '24h'
export type ScreenShareQuality = 'balanced' | 'sharp' | 'smooth'

const PREFERENCES_STORAGE_KEY = 'discord-clone-preferences'

type PersistedPreferences = {
  language?: AppLanguage
  mutedDmIds?: number[]
  favoriteFriendIds?: number[]
  theme?: AppTheme
  density?: AppDensity
  reduceMotion?: boolean
  timeFormat?: TimeFormat
  notificationMode?: NotificationMode
  soundEffects?: boolean
  dmSafety?: boolean
  friendRequestPolicy?: FriendRequestPolicy
  allowUnknownDms?: boolean
  showActivityStatus?: boolean
  screenShareQuality?: ScreenShareQuality
}

function isAppLanguage(value: unknown): value is AppLanguage {
  return value === 'ko' || value === 'en'
}

function isAppTheme(value: unknown): value is AppTheme {
  return value === 'dark' || value === 'darker'
}

function isAppDensity(value: unknown): value is AppDensity {
  return value === 'comfortable' || value === 'compact'
}

function isNotificationMode(value: unknown): value is NotificationMode {
  return value === 'all' || value === 'mentions' || value === 'none'
}

function isFriendRequestPolicy(value: unknown): value is FriendRequestPolicy {
  return value === 'everyone' || value === 'friends_of_friends' || value === 'none'
}

function isTimeFormat(value: unknown): value is TimeFormat {
  return value === 'auto' || value === '24h'
}

function isScreenShareQuality(value: unknown): value is ScreenShareQuality {
  return value === 'balanced' || value === 'sharp' || value === 'smooth'
}

export const usePreferencesStore = defineStore('preferences', () => {
  const language = ref<AppLanguage>('ko')
  const mutedDmIds = ref<number[]>([])
  const favoriteFriendIds = ref<number[]>([])
  const theme = ref<AppTheme>('dark')
  const density = ref<AppDensity>('comfortable')
  const reduceMotion = ref(false)
  const timeFormat = ref<TimeFormat>('auto')
  const notificationMode = ref<NotificationMode>('all')
  const soundEffects = ref(true)
  const dmSafety = ref(true)
  const friendRequestPolicy = ref<FriendRequestPolicy>('everyone')
  const allowUnknownDms = ref(true)
  const showActivityStatus = ref(true)
  const screenShareQuality = ref<ScreenShareQuality>('balanced')

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
      if (Array.isArray(preferences.favoriteFriendIds)) {
        favoriteFriendIds.value = preferences.favoriteFriendIds.filter((id): id is number => Number.isSafeInteger(id))
      }
      if (isAppTheme(preferences.theme)) {
        theme.value = preferences.theme
      }
      if (isAppDensity(preferences.density)) {
        density.value = preferences.density
      }
      if (typeof preferences.reduceMotion === 'boolean') {
        reduceMotion.value = preferences.reduceMotion
      }
      if (isTimeFormat(preferences.timeFormat)) {
        timeFormat.value = preferences.timeFormat
      }
      if (isNotificationMode(preferences.notificationMode)) {
        notificationMode.value = preferences.notificationMode
      }
      if (typeof preferences.soundEffects === 'boolean') {
        soundEffects.value = preferences.soundEffects
      }
      if (typeof preferences.dmSafety === 'boolean') {
        dmSafety.value = preferences.dmSafety
      }
      if (isFriendRequestPolicy(preferences.friendRequestPolicy)) {
        friendRequestPolicy.value = preferences.friendRequestPolicy
      }
      if (typeof preferences.allowUnknownDms === 'boolean') {
        allowUnknownDms.value = preferences.allowUnknownDms
      }
      if (typeof preferences.showActivityStatus === 'boolean') {
        showActivityStatus.value = preferences.showActivityStatus
      }
      if (isScreenShareQuality(preferences.screenShareQuality)) {
        screenShareQuality.value = preferences.screenShareQuality
      }
    } catch {
      browserStorage.removeItem(PREFERENCES_STORAGE_KEY)
    }
  }

  function persistPreferences() {
    const preferences: PersistedPreferences = {
      language: language.value,
      mutedDmIds: mutedDmIds.value,
      favoriteFriendIds: favoriteFriendIds.value,
      theme: theme.value,
      density: density.value,
      reduceMotion: reduceMotion.value,
      timeFormat: timeFormat.value,
      notificationMode: notificationMode.value,
      soundEffects: soundEffects.value,
      dmSafety: dmSafety.value,
      friendRequestPolicy: friendRequestPolicy.value,
      allowUnknownDms: allowUnknownDms.value,
      showActivityStatus: showActivityStatus.value,
      screenShareQuality: screenShareQuality.value,
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

  function isFavoriteFriend(friendId: number | null) {
    return friendId !== null && favoriteFriendIds.value.includes(friendId)
  }

  function setFavoriteFriend(friendId: number, favorite: boolean) {
    favoriteFriendIds.value = favorite
      ? Array.from(new Set([...favoriteFriendIds.value, friendId]))
      : favoriteFriendIds.value.filter((id) => id !== friendId)
    persistPreferences()
  }

  function toggleFavoriteFriend(friendId: number) {
    setFavoriteFriend(friendId, !isFavoriteFriend(friendId))
  }

  function setTheme(nextTheme: AppTheme) {
    theme.value = nextTheme
    persistPreferences()
  }

  function setDensity(nextDensity: AppDensity) {
    density.value = nextDensity
    persistPreferences()
  }

  function setReduceMotion(enabled: boolean) {
    reduceMotion.value = enabled
    persistPreferences()
  }

  function setTimeFormat(nextTimeFormat: TimeFormat) {
    timeFormat.value = nextTimeFormat
    persistPreferences()
  }

  function setNotificationMode(nextMode: NotificationMode) {
    notificationMode.value = nextMode
    persistPreferences()
  }

  function setSoundEffects(enabled: boolean) {
    soundEffects.value = enabled
    persistPreferences()
  }

  function setDmSafety(enabled: boolean) {
    dmSafety.value = enabled
    persistPreferences()
  }

  function setFriendRequestPolicy(policy: FriendRequestPolicy) {
    friendRequestPolicy.value = policy
    persistPreferences()
  }

  function setAllowUnknownDms(enabled: boolean) {
    allowUnknownDms.value = enabled
    persistPreferences()
  }

  function setShowActivityStatus(enabled: boolean) {
    showActivityStatus.value = enabled
    persistPreferences()
  }

  function setScreenShareQuality(quality: ScreenShareQuality) {
    screenShareQuality.value = quality
    persistPreferences()
  }

  return {
    language,
    mutedDmIds,
    favoriteFriendIds,
    theme,
    density,
    reduceMotion,
    timeFormat,
    notificationMode,
    soundEffects,
    dmSafety,
    friendRequestPolicy,
    allowUnknownDms,
    showActivityStatus,
    screenShareQuality,
    restorePreferences,
    setLanguage,
    isDmMuted,
    setDmMuted,
    toggleDmMuted,
    isFavoriteFriend,
    setFavoriteFriend,
    toggleFavoriteFriend,
    setTheme,
    setDensity,
    setReduceMotion,
    setTimeFormat,
    setNotificationMode,
    setSoundEffects,
    setDmSafety,
    setFriendRequestPolicy,
    setAllowUnknownDms,
    setShowActivityStatus,
    setScreenShareQuality,
  }
})
