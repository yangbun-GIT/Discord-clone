<script setup lang="ts">
import { computed, ref } from 'vue'
import { FlaskConical, LogIn, UserPlus } from 'lucide-vue-next'

type AuthMode = 'login' | 'register'

const emit = defineEmits<{
  login: [payload: { username: string; password: string }]
  register: [payload: { username: string; password: string }]
  demo: []
}>()

defineProps<{
  error?: string | null
  loading?: boolean
}>()

const mode = ref<AuthMode>('login')
const username = ref('')
const password = ref('')

const submitLabel = computed(() => (mode.value === 'login' ? 'Log in' : 'Create account'))
const isSubmittable = computed(() => username.value.trim().length >= 2 && password.value.length >= 8)

function submit() {
  if (!isSubmittable.value) return
  const payload = { username: username.value.trim(), password: password.value }
  if (mode.value === 'login') {
    emit('login', payload)
    return
  }
  emit('register', payload)
}
</script>

<template>
  <main class="auth-shell" aria-label="Discord clone authentication">
    <section class="auth-panel">
      <div class="auth-mark">DC</div>

      <div class="auth-tabs" role="tablist" aria-label="Authentication mode">
        <button
          type="button"
          :class="{ active: mode === 'login' }"
          role="tab"
          :aria-selected="mode === 'login'"
          @click="mode = 'login'"
        >
          <LogIn :size="17" aria-hidden="true" />
          <span>Log in</span>
        </button>
        <button
          type="button"
          :class="{ active: mode === 'register' }"
          role="tab"
          :aria-selected="mode === 'register'"
          @click="mode = 'register'"
        >
          <UserPlus :size="17" aria-hidden="true" />
          <span>Register</span>
        </button>
      </div>

      <form class="auth-form" @submit.prevent="submit">
        <label>
          <span>Username</span>
          <input v-model="username" autocomplete="username" minlength="2" maxlength="32" required />
        </label>

        <label>
          <span>Password</span>
          <input
            v-model="password"
            autocomplete="current-password"
            minlength="8"
            maxlength="128"
            required
            type="password"
          />
        </label>

        <button type="submit" :disabled="!isSubmittable || loading">
          {{ submitLabel }}
        </button>
      </form>

      <p v-if="error" class="auth-error" role="alert">{{ error }}</p>

      <button class="demo-button" type="button" :disabled="loading" @click="emit('demo')">
        <FlaskConical :size="17" aria-hidden="true" />
        <span>Demo user</span>
      </button>
    </section>
  </main>
</template>
