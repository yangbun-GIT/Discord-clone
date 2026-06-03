<script setup lang="ts">
import { ref, watch } from 'vue'
import { Compass, LogIn, Plus, X } from 'lucide-vue-next'

const props = defineProps<{
  initialMode: 'create' | 'join'
  loading: boolean
}>()

const emit = defineEmits<{
  close: []
  create: [name: string]
  join: [code: string]
  discover: []
}>()

const mode = ref(props.initialMode)
const serverName = ref('')
const inviteCode = ref('')

watch(
  () => props.initialMode,
  (nextMode) => {
    mode.value = nextMode
  },
)

function submit() {
  if (mode.value === 'create') {
    const name = serverName.value.trim()
    if (!name) return
    emit('create', name)
    return
  }
  const code = inviteCode.value.trim()
  if (!code) return
  emit('join', code)
}
</script>

<template>
  <section class="modal-layer" aria-label="Add server">
    <form class="server-add-dialog" @submit.prevent="submit">
      <header class="server-add-header">
        <div>
          <div class="auth-mark">DC</div>
          <h2>Add a Server</h2>
        </div>
        <button type="button" title="Close" aria-label="Close" @click="$emit('close')">
          <X :size="18" aria-hidden="true" />
        </button>
      </header>

      <div class="server-add-tabs" role="tablist" aria-label="Add server mode">
        <button
          type="button"
          role="tab"
          :aria-selected="mode === 'create'"
          :class="{ active: mode === 'create' }"
          @click="mode = 'create'"
        >
          <Plus :size="17" aria-hidden="true" />
          <span>Create</span>
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="mode === 'join'"
          :class="{ active: mode === 'join' }"
          @click="mode = 'join'"
        >
          <LogIn :size="17" aria-hidden="true" />
          <span>Join</span>
        </button>
      </div>

      <label v-if="mode === 'create'">
        <span>Server name</span>
        <input v-model="serverName" autocomplete="off" maxlength="100" minlength="2" required autofocus />
      </label>
      <label v-else>
        <span>Invite code</span>
        <input v-model="inviteCode" autocomplete="off" required autofocus />
      </label>

      <button type="button" class="server-discovery-link" @click="$emit('discover')">
        <Compass :size="17" aria-hidden="true" />
        <span>Explore public demo servers</span>
      </button>

      <div class="dialog-actions">
        <button type="button" @click="$emit('close')">Cancel</button>
        <button
          type="submit"
          :disabled="loading || (mode === 'create' ? serverName.trim().length < 2 : !inviteCode.trim())"
        >
          {{ mode === 'create' ? 'Create' : 'Join' }}
        </button>
      </div>
    </form>
  </section>
</template>
