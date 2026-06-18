import { computed } from 'vue'

import type { TranslationKey } from '../i18n'
import type { Channel, DirectMessage, Guild } from '../types'

interface WorkspaceControllerOptions {
  destination: () => string
  activeGuild: () => Guild | null
  activeChannel: () => Channel | null
  selectedDm: () => DirectMessage | null | undefined
  voiceConnected: () => boolean
  connectedVoiceGuild: () => Guild | null
  connectedVoiceChannel: () => Channel | null
  isDeafened: () => boolean
  isMuted: () => boolean
  localSpeaking: () => boolean
  t: (key: TranslationKey) => string
}

export function useWorkspaceController(options: WorkspaceControllerOptions) {
  const workspaceTitle = computed(() => {
    if (options.destination() === 'friends') return options.t('app.status.friends')
    if (options.destination() === 'dm') {
      return options.selectedDm()?.display_name ?? options.t('app.status.directMessage')
    }
    if (options.destination() === 'settings') return options.t('app.status.userSettings')
    if (!options.activeGuild()) return options.t('app.status.noServers')
    return options.activeChannel()?.name ?? options.t('app.status.loading')
  })

  const workspaceSubtitle = computed(() => {
    if (options.destination() === 'friends') return options.t('app.location.privateHome')
    if (options.destination() === 'dm') return options.t('app.location.directMessage')
    if (options.destination() === 'settings') return options.t('app.location.settings')
    const guild = options.activeGuild()
    if (!guild) return options.t('app.location.noServer')
    const channelKind = options.activeChannel()?.type === 1
      ? options.t('app.location.voiceChannel')
      : options.t('app.location.textChannel')
    return `${guild.name} / ${channelKind}`
  })

  const voiceLocationSummary = computed(() => {
    const voiceGuild = options.connectedVoiceGuild()
    const voiceChannel = options.connectedVoiceChannel()
    if (!options.voiceConnected() || !voiceChannel || !voiceGuild) return null
    const state = options.isDeafened()
      ? options.t('common.status.deafened')
      : options.isMuted()
        ? options.t('common.status.muted')
        : options.localSpeaking()
          ? options.t('voice.speaking')
          : options.t('common.status.connected')
    return `${voiceGuild.name} / ${voiceChannel.name} · ${state}`
  })

  return {
    workspaceTitle,
    workspaceSubtitle,
    voiceLocationSummary,
  }
}
