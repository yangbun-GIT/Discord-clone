import { ref } from 'vue'

export type GlobalNoticeTone = 'info' | 'success' | 'warning'

export function useGlobalNotice(options: { onShow?: () => void } = {}) {
  const notice = ref<string | null>(null)
  const tone = ref<GlobalNoticeTone>('info')
  const timer = ref<number | null>(null)

  function clearNotice() {
    if (timer.value) {
      window.clearTimeout(timer.value)
      timer.value = null
    }
    notice.value = null
  }

  function setNotice(message: string, nextTone: GlobalNoticeTone = 'info') {
    if (timer.value) {
      window.clearTimeout(timer.value)
      timer.value = null
    }
    options.onShow?.()
    tone.value = nextTone
    notice.value = message
    timer.value = window.setTimeout(() => {
      notice.value = null
      timer.value = null
    }, 3600)
  }

  return {
    notice,
    tone,
    setNotice,
    clearNotice,
  }
}
