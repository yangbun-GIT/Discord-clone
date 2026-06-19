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

watch(
  () => [video.value, props.stream] as const,
  ([element, stream]) => {
    if (element) {
      element.srcObject = stream
    }
  },
  { immediate: true },
)
</script>

<template>
  <article class="screen-share-tile" :data-state="state" :data-user-id="userId ?? null">
    <video ref="video" autoplay playsinline />
    <div>
      <strong>{{ label }}</strong>
      <span v-if="subtitle">{{ subtitle }}</span>
    </div>
  </article>
</template>
