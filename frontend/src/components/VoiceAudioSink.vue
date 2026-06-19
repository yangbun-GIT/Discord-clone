<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  stream: MediaStream
  muted: boolean
}>()

const audio = ref<HTMLAudioElement | null>(null)

watch(
  () => [audio.value, props.stream, props.muted] as const,
  ([element, stream, muted]) => {
    if (element) {
      element.srcObject = stream
      element.muted = muted
    }
  },
  { immediate: true },
)
</script>

<template>
  <audio ref="audio" autoplay playsinline :muted="muted" :data-deafened="muted" />
</template>
