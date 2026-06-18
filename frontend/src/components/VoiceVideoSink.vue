<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  stream: MediaStream
  label: string
  state: string
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
  <article class="screen-share-tile" :data-state="state">
    <video ref="video" autoplay playsinline />
    <div>
      <strong>{{ label }}</strong>
    </div>
  </article>
</template>
