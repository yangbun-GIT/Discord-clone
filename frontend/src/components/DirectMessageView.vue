<script setup lang="ts">
import { ArrowDown, BellOff, ChevronUp, HeadphoneOff, Laugh, Mic, MicOff, Phone, PhoneOff, Send, Trash2, UserRound, Volume2 } from 'lucide-vue-next'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import { useI18n } from '../i18n'
import type { VoiceDeviceList, VoiceDeviceSettings } from '../composables/voiceMedia'
import { addDocumentEventListener } from '../services/browserApi'
import type { DirectMessage, User } from '../types'

const props = defineProps<{
  dm: DirectMessage | null
  currentUser: User | null
  disabled: boolean
  muted?: boolean
  voiceMuted?: boolean
  deafened?: boolean
  callActive?: boolean
  callJoinable?: boolean
  voiceDeviceSettings: VoiceDeviceSettings
  voiceDevices: VoiceDeviceList
}>()

const draft = ref('')
const showEmojiPanel = ref(false)
const audioMenu = ref<'input' | 'output' | null>(null)
const messageList = ref<HTMLElement | null>(null)
const composerInput = ref<HTMLInputElement | null>(null)
const showJumpToLatest = ref(false)
const pendingComposerFocusRestore = ref(false)
const { t } = useI18n()
const SNOWFLAKE_CUSTOM_EPOCH_MS = Date.UTC(2026, 0, 1)
const SNOWFLAKE_TIMESTAMP_SHIFT = 14
let removeDocumentPointerDown: (() => void) | null = null
let removeDocumentKeyDown: (() => void) | null = null
const emojiOptions = ['😀', '😂', '👍', '🎉', '🔥', '💬', '✨', '🙌']

const emit = defineEmits<{
  send: [content: string]
  viewProfile: []
  startCall: []
  leaveCall: []
  toggleMute: []
  toggleVoiceMute: []
  toggleDeafen: []
  openVoiceSettings: []
  refreshVoiceDevices: []
  updateVoiceDeviceSettings: [settings: Partial<VoiceDeviceSettings>]
  deleteMessage: [messageId: number]
}>()

function submitMessage() {
  const content = draft.value.trim()
  if (!content || props.disabled || !props.dm) return
  emit('send', content)
  draft.value = ''
  showEmojiPanel.value = false
  restoreComposerFocus()
}

function insertEmoji(emoji: string) {
  draft.value = `${draft.value}${draft.value ? ' ' : ''}${emoji}`.slice(0, 2000)
  restoreComposerFocus()
}

function restoreComposerFocus() {
  pendingComposerFocusRestore.value = true
  void nextTick(() => {
    focusComposerInput()
    window.requestAnimationFrame(focusComposerInput)
    window.setTimeout(focusComposerInput, 0)
  })
}

function focusComposerInput() {
  if (!pendingComposerFocusRestore.value || props.disabled || !props.dm) return
  const input = composerInput.value
  if (!input) return
  input.focus({ preventScroll: true })
  const cursorPosition = input.value.length
  input.setSelectionRange(cursorPosition, cursorPosition)
  pendingComposerFocusRestore.value = false
}

function toggleAudioMenu(menu: 'input' | 'output') {
  if (audioMenu.value === menu) {
    audioMenu.value = null
    return
  }
  audioMenu.value = menu
  emit('refreshVoiceDevices')
}

function handleDeviceSelect(key: 'inputDeviceId' | 'outputDeviceId', event: Event) {
  const target = event.target
  if (!(target instanceof HTMLSelectElement)) return
  emit('updateVoiceDeviceSettings', { [key]: target.value || null })
}

function handleDeviceRange(
  key: 'inputVolume' | 'outputVolume' | 'inputSensitivity',
  event: Event,
) {
  const target = event.target
  if (!(target instanceof HTMLInputElement)) return
  emit('updateVoiceDeviceSettings', { [key]: Number(target.value) })
}

function handleNoiseGateChange(event: Event) {
  const target = event.target
  if (!(target instanceof HTMLInputElement)) return
  emit('updateVoiceDeviceSettings', { noiseGate: target.checked })
}

function handleNoiseSuppressionModeChange(event: Event) {
  const target = event.target
  if (!(target instanceof HTMLSelectElement)) return
  const mode = target.value
  if (mode !== 'off' && mode !== 'rnnoise') return
  emit('updateVoiceDeviceSettings', {
    noiseSuppressionMode: mode,
    rnnoiseSuppression: mode === 'rnnoise',
  })
}

const otherParticipants = computed(() =>
  props.dm?.participants.filter((participant) => participant.id !== props.currentUser?.id) ?? [],
)

const primaryParticipant = computed(() => otherParticipants.value[0] ?? null)

const primaryParticipantStatusLabel = computed(() => {
  switch (primaryParticipant.value?.status ?? props.dm?.status ?? 'offline') {
    case 'online':
      return t('common.status.online')
    case 'idle':
      return t('common.status.idle')
    case 'dnd':
      return t('common.status.dnd')
    case 'offline':
    default:
      return t('common.status.offline')
  }
})

function isOwnMessage(authorId: number) {
  return props.currentUser?.id === authorId
}

function deleteMessage(messageId: number) {
  if (props.disabled || !props.dm) return
  emit('deleteMessage', messageId)
}

function isNearBottom() {
  const element = messageList.value
  if (!element) return true
  return element.scrollHeight - element.scrollTop - element.clientHeight < 96
}

function scrollToLatest(behavior: ScrollBehavior = 'auto') {
  const element = messageList.value
  if (!element) return
  element.scrollTo({ top: element.scrollHeight, behavior })
  showJumpToLatest.value = false
}

function handleMessageScroll() {
  showJumpToLatest.value = !isNearBottom()
}

function messageDate(message: DirectMessage['messages'][number]) {
  if (message.created_at) {
    const timestamp = new Date(message.created_at)
    if (!Number.isNaN(timestamp.getTime())) return timestamp
  }
  return new Date(Math.floor(message.id / 2 ** SNOWFLAKE_TIMESTAMP_SHIFT) + SNOWFLAKE_CUSTOM_EPOCH_MS)
}

function messageTime(message: DirectMessage['messages'][number]) {
  return new Intl.DateTimeFormat(undefined, { hour: 'numeric', minute: '2-digit' }).format(
    messageDate(message),
  )
}

function messageDateKey(message: DirectMessage['messages'][number]) {
  const date = messageDate(message)
  return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`
}

function messageDateLabel(message: DirectMessage['messages'][number]) {
  return new Intl.DateTimeFormat(undefined, { year: 'numeric', month: 'long', day: 'numeric' }).format(
    messageDate(message),
  )
}

function shouldShowMessageDateDivider(message: DirectMessage['messages'][number], index: number) {
  if (index === 0 || !props.dm) return false
  const previousMessage = props.dm.messages[index - 1]
  if (!previousMessage) return false
  return messageDateKey(previousMessage) !== messageDateKey(message)
}

const timelineDate = computed(() => {
  const firstMessage = props.dm?.messages[0]
  const date = firstMessage ? messageDate(firstMessage) : new Date()
  return new Intl.DateTimeFormat(undefined, { year: 'numeric', month: 'long', day: 'numeric' }).format(date)
})

watch(
  () => props.dm?.id,
  () => {
    draft.value = ''
    showEmojiPanel.value = false
    pendingComposerFocusRestore.value = false
    void nextTick(() => scrollToLatest())
  },
)

watch(
  () => props.disabled,
  (isDisabled) => {
    if (!isDisabled && pendingComposerFocusRestore.value) restoreComposerFocus()
  },
)

watch(
  () => props.dm?.messages.length ?? 0,
  async () => {
    const shouldStick = !showJumpToLatest.value && isNearBottom()
    await nextTick()
    if (shouldStick) scrollToLatest()
  },
)

function handleDocumentPointerDown(event: MouseEvent) {
  const target = event.target
  const element = target instanceof HTMLElement ? target : null
  if (showEmojiPanel.value && !element?.closest('.composer-shell')) {
    showEmojiPanel.value = false
  }
  if (audioMenu.value && !element?.closest('.dm-call-device-popover, .dm-call-device-controls')) {
    audioMenu.value = null
  }
}

function handleDocumentKeyDown(event: KeyboardEvent) {
  if (event.key !== 'Escape') return
  showEmojiPanel.value = false
  audioMenu.value = null
}

onMounted(() => {
  removeDocumentPointerDown = addDocumentEventListener('mousedown', handleDocumentPointerDown)
  removeDocumentKeyDown = addDocumentEventListener('keydown', handleDocumentKeyDown)
  void nextTick(() => scrollToLatest())
})

onBeforeUnmount(() => {
  removeDocumentPointerDown?.()
  removeDocumentKeyDown?.()
  removeDocumentPointerDown = null
  removeDocumentKeyDown = null
})
</script>

<template>
  <section class="chat-view" :aria-label="t('dm.aria.directMessages')">
    <div ref="messageList" class="message-list message-list-bottom" @scroll="handleMessageScroll">
      <section v-if="dm && (callActive || callJoinable)" class="dm-call-stage" :aria-label="t('dm.callActive')">
        <div class="dm-call-avatars" aria-hidden="true">
          <span class="dm-call-avatar local">{{ currentUser?.username.slice(0, 1).toUpperCase() ?? 'Y' }}</span>
          <span
            v-for="participant in otherParticipants.slice(0, 2)"
            :key="participant.id"
            class="dm-call-avatar"
          >
            {{ participant.username.slice(0, 1).toUpperCase() }}
          </span>
        </div>
        <div>
          <strong>{{ dm.display_name }}</strong>
          <span>{{ callActive ? t('dm.callConnected') : t('friends.incomingDmCallDescription') }}</span>
        </div>
        <div v-if="callActive" class="dm-call-control-stack">
          <div class="dm-call-device-controls" :aria-label="t('voice.aria.controls')">
            <span class="dm-call-control-cluster">
              <button
                type="button"
                :title="voiceMuted ? t('voice.unmute') : t('voice.mute')"
                :aria-label="voiceMuted ? t('voice.unmute') : t('voice.mute')"
                :aria-pressed="voiceMuted"
                @click="$emit('toggleVoiceMute')"
              >
                <MicOff v-if="voiceMuted" :size="17" aria-hidden="true" />
                <Mic v-else :size="17" aria-hidden="true" />
              </button>
              <button
                type="button"
                class="dm-call-popover-trigger"
                :title="t('voice.openInputMenu')"
                :aria-label="t('voice.openInputMenu')"
                :aria-expanded="audioMenu === 'input'"
                @click="toggleAudioMenu('input')"
              >
                <ChevronUp :size="13" aria-hidden="true" />
              </button>
            </span>
            <span class="dm-call-control-cluster">
              <button
                type="button"
                :title="deafened ? t('voice.undeafen') : t('voice.deafen')"
                :aria-label="deafened ? t('voice.undeafen') : t('voice.deafen')"
                :aria-pressed="deafened"
                @click="$emit('toggleDeafen')"
              >
                <HeadphoneOff v-if="deafened" :size="17" aria-hidden="true" />
                <Volume2 v-else :size="17" aria-hidden="true" />
              </button>
              <button
                type="button"
                class="dm-call-popover-trigger"
                :title="t('voice.openOutputMenu')"
                :aria-label="t('voice.openOutputMenu')"
                :aria-expanded="audioMenu === 'output'"
                @click="toggleAudioMenu('output')"
              >
                <ChevronUp :size="13" aria-hidden="true" />
              </button>
            </span>
            <button
              type="button"
              class="dm-call-leave"
              :aria-label="t('voice.leaveSelected')"
              @click="$emit('leaveCall')"
            >
              <PhoneOff :size="18" aria-hidden="true" />
            </button>
          </div>
          <div
            v-if="audioMenu"
            class="dm-call-device-popover"
            :aria-label="audioMenu === 'input' ? t('voice.inputMenu') : t('voice.outputMenu')"
          >
            <template v-if="audioMenu === 'input'">
              <label class="voice-device-field">
                <span>{{ t('settings.inputDevice') }}</span>
                <select
                  :value="voiceDeviceSettings.inputDeviceId ?? ''"
                  @change="handleDeviceSelect('inputDeviceId', $event)"
                >
                  <option value="">{{ t('settings.defaultDevice') }}</option>
                  <option v-for="device in voiceDevices.inputs" :key="device.id" :value="device.id">
                    {{ device.label }}
                  </option>
                </select>
              </label>
              <label class="voice-device-range">
                <span>{{ t('settings.inputVolume') }}</span>
                <input
                  type="range"
                  min="0"
                  max="100"
                  :value="voiceDeviceSettings.inputVolume"
                  @input="handleDeviceRange('inputVolume', $event)"
                />
                <strong>{{ voiceDeviceSettings.inputVolume }}%</strong>
              </label>
              <label class="voice-device-range voice-device-sensitivity">
                <span>{{ t('settings.inputSensitivity') }}</span>
                <input
                  type="range"
                  min="5"
                  max="85"
                  :value="voiceDeviceSettings.inputSensitivity"
                  @input="handleDeviceRange('inputSensitivity', $event)"
                />
                <strong>{{ voiceDeviceSettings.inputSensitivity }}%</strong>
              </label>
              <label class="voice-device-field">
                <span>{{ t('settings.noiseSuppressionEngine') }}</span>
                <select
                  :value="voiceDeviceSettings.noiseSuppressionMode"
                  @change="handleNoiseSuppressionModeChange"
                >
                  <option value="off">{{ t('settings.noiseSuppressionOff') }}</option>
                  <option value="rnnoise">{{ t('settings.rnnoiseSuppression') }}</option>
                </select>
              </label>
              <label class="voice-device-toggle">
                <span>{{ t('settings.noiseGate') }}</span>
                <input
                  type="checkbox"
                  :checked="voiceDeviceSettings.noiseGate"
                  @change="handleNoiseGateChange"
                />
              </label>
            </template>
            <template v-else>
              <label class="voice-device-field">
                <span>{{ t('settings.outputDevice') }}</span>
                <select
                  :value="voiceDeviceSettings.outputDeviceId ?? ''"
                  @change="handleDeviceSelect('outputDeviceId', $event)"
                >
                  <option value="">{{ t('settings.defaultDevice') }}</option>
                  <option v-for="device in voiceDevices.outputs" :key="device.id" :value="device.id">
                    {{ device.label }}
                  </option>
                </select>
              </label>
              <label class="voice-device-range">
                <span>{{ t('settings.outputVolume') }}</span>
                <input
                  type="range"
                  min="0"
                  max="100"
                  :value="voiceDeviceSettings.outputVolume"
                  @input="handleDeviceRange('outputVolume', $event)"
                />
                <strong>{{ voiceDeviceSettings.outputVolume }}%</strong>
              </label>
            </template>
          </div>
        </div>
        <button
          v-else
          type="button"
          class="dm-call-join"
          :aria-label="t('friends.acceptCall')"
          @click="$emit('startCall')"
        >
          <Phone :size="18" aria-hidden="true" />
          <span>{{ t('friends.acceptCall') }}</span>
        </button>
      </section>

      <div class="dm-thread-stack">
        <section v-if="dm" class="dm-chat-intro" :aria-label="t('dm.aria.conversation')">
          <div class="dm-intro-heading">
            <div class="dm-placeholder-avatar">
              {{ dm.display_name.slice(0, 1).toUpperCase() }}
            </div>
            <div class="dm-intro-title">
              <h2>{{ dm.display_name }}</h2>
              <p v-if="dm.is_group">{{ t('dm.groupDescription', { count: dm.member_count }) }}</p>
              <p v-else>{{ t('dm.beginning') }}</p>
            </div>
          </div>
          <div v-if="otherParticipants.length" class="dm-participant-strip" :aria-label="t('dm.participants')">
            <span v-if="!dm.is_group" :class="['status-pill', `status-${primaryParticipant?.status ?? dm.status}`]">
              {{ primaryParticipantStatusLabel }}
            </span>
            <span v-for="participant in dm.is_group ? otherParticipants : []" :key="participant.id">
              {{ participant.username }}
            </span>
          </div>
          <div class="dm-header-actions" :aria-label="t('dm.headerActions')">
            <button type="button" :disabled="disabled" @click="$emit('viewProfile')">
              <UserRound :size="16" aria-hidden="true" />
              <span>{{ t('friends.viewProfile') }}</span>
            </button>
            <button type="button" :disabled="disabled" @click="$emit('startCall')">
              <Phone :size="16" aria-hidden="true" />
              <span>{{ t('friends.startCall') }}</span>
            </button>
            <button type="button" :class="{ active: muted }" :disabled="disabled" @click="$emit('toggleMute')">
              <BellOff :size="16" aria-hidden="true" />
              <span>{{ muted ? t('friends.unmuteConversation') : t('friends.muteConversation') }}</span>
            </button>
          </div>
          <div v-if="dm.messages.length" class="date-divider dm-date-divider"><span>{{ timelineDate }}</span></div>
        </section>

        <section v-else class="dm-chat-intro" :aria-label="t('dm.aria.noSelection')">
          <div class="dm-placeholder-avatar">D</div>
          <h2>{{ t('app.status.directMessage') }}</h2>
          <p>{{ t('dm.selectConversation') }}</p>
        </section>

        <template v-for="(message, index) in dm?.messages ?? []" :key="message.id">
          <div v-if="shouldShowMessageDateDivider(message, index)" class="date-divider dm-date-divider">
            <span>{{ messageDateLabel(message) }}</span>
          </div>
          <article
            :class="['message-row', 'dm-message-row', { own: isOwnMessage(message.author_id), remote: !isOwnMessage(message.author_id) }]"
            tabindex="0"
            data-context-kind="dm-message"
            :data-context-label="message.author_name"
          >
            <div class="avatar" aria-hidden="true">
              {{ message.author_name.slice(0, 1).toUpperCase() }}
            </div>
            <div class="message-main">
              <div class="message-meta">
                <strong>{{ message.author_name }}</strong>
                <span>{{ messageTime(message) }}</span>
                <span v-if="isOwnMessage(message.author_id)">{{ t('channel.you') }}</span>
                <div v-if="isOwnMessage(message.author_id)" class="message-actions" :aria-label="t('chat.aria.messageActions')">
                  <button
                    class="message-icon-button danger"
                    type="button"
                    :title="t('chat.deleteMessage')"
                    :aria-label="t('chat.deleteMessage')"
                    @click="deleteMessage(message.id)"
                  >
                    <Trash2 :size="14" aria-hidden="true" />
                  </button>
                </div>
              </div>
              <p>{{ message.content }}</p>
            </div>
          </article>
        </template>
      </div>
    </div>

    <button
      v-if="showJumpToLatest"
      type="button"
      class="jump-to-latest"
      @click="scrollToLatest('smooth')"
    >
      <ArrowDown :size="15" aria-hidden="true" />
      <span>{{ t('chat.jumpToLatest') }}</span>
    </button>

    <section class="composer-shell" :aria-label="t('chat.aria.composer')">
      <form class="composer dm-composer" @submit.prevent="submitMessage">
        <input
          ref="composerInput"
          v-model="draft"
          :aria-label="t('dm.messageTarget', { target: dm?.display_name ?? t('app.status.directMessage') })"
          :placeholder="dm ? t('dm.messageTarget', { target: dm.display_name }) : t('dm.selectPlaceholder')"
          maxlength="2000"
          :disabled="disabled || !dm"
        />
        <div class="composer-actions composer-secondary-actions" :aria-label="t('chat.aria.expressionActions')">
          <button
            type="button"
            :title="t('chat.emoji')"
            :aria-label="t('chat.emoji')"
            :aria-expanded="showEmojiPanel"
            :disabled="disabled || !dm"
            @click="showEmojiPanel = !showEmojiPanel"
          >
            <Laugh :size="18" aria-hidden="true" />
          </button>
        </div>
        <button
          class="composer-send-button"
          type="submit"
          :title="t('chat.sendMessage')"
          :disabled="disabled || !dm || !draft.trim()"
          @pointerdown.prevent
        >
          <Send :size="18" aria-hidden="true" />
        </button>
      </form>
      <div v-if="showEmojiPanel" class="composer-demo-panel" role="status">
        <div class="composer-panel-copy">
          <strong>{{ t('chat.demoPanel.title', { label: t('chat.emoji') }) }}</strong>
          <span>{{ t('chat.emojiDescription') }}</span>
        </div>
        <div class="composer-emoji-grid">
          <button v-for="emoji in emojiOptions" :key="emoji" type="button" @click="insertEmoji(emoji)">
            {{ emoji }}
          </button>
        </div>
        <button type="button" @click="showEmojiPanel = false">{{ t('common.close') }}</button>
      </div>
    </section>
  </section>
</template>
