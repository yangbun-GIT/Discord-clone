import { defineStore } from 'pinia'
import { ref } from 'vue'

export type AppDestination = 'friends' | 'dm' | 'server_channel' | 'voice_channel' | 'settings'

export const useNavigationStore = defineStore('navigation', () => {
  const destination = ref<AppDestination>('friends')
  const activeDmId = ref<number | null>(null)

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
    destination.value = 'settings'
  }

  function resetNavigation() {
    destination.value = 'friends'
    activeDmId.value = null
  }

  return {
    destination,
    activeDmId,
    openFriends,
    openDm,
    openServerChannel,
    openVoiceChannel,
    openSettings,
    resetNavigation,
  }
})
