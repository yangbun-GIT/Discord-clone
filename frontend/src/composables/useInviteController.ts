import { computed, ref } from 'vue'

import type { Friend } from '../types'

export function useInviteController(relationships: () => Friend[]) {
  const showInvite = ref(false)
  const inviteCode = ref<string | null>(null)
  const inviteSearchQuery = ref('')
  const inviteCopied = ref(false)

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
    inviteCopied.value = false
    showInvite.value = true
  }

  function closeInvite() {
    showInvite.value = false
    inviteCode.value = null
    inviteSearchQuery.value = ''
    inviteCopied.value = false
  }

  return {
    showInvite,
    inviteCode,
    inviteSearchQuery,
    inviteCopied,
    inviteFriends,
    openInvite,
    closeInvite,
  }
}
