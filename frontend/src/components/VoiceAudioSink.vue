<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  stream: MediaStream
  muted: boolean
  outputDeviceId: string | null
  volume: number
}>()

const audio = ref<HTMLAudioElement | null>(null)

watch(
  () => [audio.value, props.stream, props.muted, props.outputDeviceId, props.volume] as const,
  ([element, stream, muted, outputDeviceId, volume]) => {
    if (element) {
      element.srcObject = stream
      element.muted = muted
      element.volume = Math.min(1, Math.max(0, volume / 100))
      const sinkElement = element as HTMLAudioElement & {
        setSinkId?: (sinkId: string) => Promise<void>
      }
      if (outputDeviceId && sinkElement.setSinkId) {
        void sinkElement.setSinkId(outputDeviceId).catch(() => {})
      }
    }
  },
  { immediate: true },
)
</script>

<template>
  <audio ref="audio" autoplay playsinline :muted="muted" :data-deafened="muted" />
</template>
