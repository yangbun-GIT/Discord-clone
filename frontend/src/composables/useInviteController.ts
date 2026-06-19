import { computed, ref } from 'vue'

import type { Friend } from '../types'

export type InviteFriendDeliveryState = 'idle' | 'sending' | 'sent' | 'error'

export function useInviteController(relationships: () => Friend[]) {
  const showInvite = ref(false)
  const inviteCode = ref<string | null>(null)
  const inviteSearchQuery = ref('')
  const inviteCodeCopied = ref(false)
  const inviteFriendStates = ref<Record<number, InviteFriendDeliveryState>>({})

  const inviteFriends = computed(() => {
    const query = inviteSearchQuery.value.trim().toLowerCase()
    return relationships()
      .filter((friend) => friend.relationship === 'friend')
      .filter((friend) => {
        if (!query) return true
        return friend.username.toLowerCase().includes(query) || friend.handle.toLowerCase().includes(query)
      })
      .slice(0, 8)
  })

  function openInvite(code: string | null) {
    inviteCode.value = code
    inviteCodeCopied.value = false
    inviteFriendStates.value = {}
    showInvite.value = true
  }

  function closeInvite() {
    showInvite.value = false
    inviteCode.value = null
    inviteSearchQuery.value = ''
    inviteCodeCopied.value = false
    inviteFriendStates.value = {}
  }

  function setInviteCodeCopied(copied: boolean) {
    inviteCodeCopied.value = copied
  }

  function setInviteFriendState(friendId: number, state: InviteFriendDeliveryState) {
    inviteFriendStates.value = {
      ...inviteFriendStates.value,
      [friendId]: state,
    }
  }

  function inviteFriendState(friendId: number) {
    return inviteFriendStates.value[friendId] ?? 'idle'
  }

  return {
    showInvite,
    inviteCode,
    inviteSearchQuery,
    inviteCodeCopied,
    inviteFriends,
    inviteFriendState,
    openInvite,
    closeInvite,
    setInviteCodeCopied,
    setInviteFriendState,
  }
}
