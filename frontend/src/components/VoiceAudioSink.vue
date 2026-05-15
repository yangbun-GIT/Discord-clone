<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  stream: MediaStream
}>()

const audio = ref<HTMLAudioElement | null>(null)

watch(
  () => [audio.value, props.stream] as const,
  ([element, stream]) => {
    if (element) {
      element.srcObject = stream
    }
  },
  { immediate: true },
)
</script>

<template>
  <audio ref="audio" autoplay playsinline />
</template>
