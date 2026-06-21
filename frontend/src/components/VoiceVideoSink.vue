<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  stream: MediaStream
  label: string
  subtitle?: string
  state: string
  userId?: number
}>()

const video = ref<HTMLVideoElement | null>(null)

function playVideo(element: HTMLVideoElement) {
  element.muted = true
  element.playsInline = true
  const playAttempt = element.play()
  if (playAttempt) {
    void playAttempt.catch(() => {
      // The next track/metadata event will retry playback.
    })
  }
}

watch(
  () => [video.value, props.stream] as const,
  ([element, stream], _previous, onCleanup) => {
    if (element) {
      const handleTrackChange = () => playVideo(element)
      const handleMetadata = () => playVideo(element)
      element.srcObject = stream
      stream.addEventListener('addtrack', handleTrackChange)
      stream.addEventListener('removetrack', handleTrackChange)
      element.addEventListener('loadedmetadata', handleMetadata)
      element.addEventListener('canplay', handleMetadata)
      playVideo(element)
      onCleanup(() => {
        stream.removeEventListener('addtrack', handleTrackChange)
        stream.removeEventListener('removetrack', handleTrackChange)
        element.removeEventListener('loadedmetadata', handleMetadata)
        element.removeEventListener('canplay', handleMetadata)
        if (element.srcObject === stream) {
          element.srcObject = null
        }
      })
    }
  },
  { immediate: true },
)
</script>

<template>
  <article class="screen-share-tile" :data-state="state" :data-user-id="userId ?? null">
    <video ref="video" autoplay muted playsinline />
    <div>
      <strong>{{ label }}</strong>
      <span v-if="subtitle">{{ subtitle }}</span>
    </div>
  </article>
</template>
