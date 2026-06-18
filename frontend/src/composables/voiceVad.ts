import type { Ref } from 'vue'

interface VoiceVadOptions {
  inputLevel: Ref<number>
  localSpeaking: Ref<boolean>
}

export function createVoiceVad(options: VoiceVadOptions) {
  let vadTimer: number | null = null
  let localAnalyser: AnalyserNode | null = null
  let audioContext: AudioContext | null = null

  function ensureAudioContext() {
    audioContext ??= new AudioContext()
    return audioContext
  }

  function attach(stream: MediaStream) {
    const context = ensureAudioContext()
    const source = context.createMediaStreamSource(stream)
    localAnalyser = context.createAnalyser()
    localAnalyser.fftSize = 512
    source.connect(localAnalyser)
  }

  function start() {
    if (vadTimer !== null || !localAnalyser) return
    const data = new Uint8Array(localAnalyser.frequencyBinCount)
    vadTimer = window.setInterval(() => {
      if (!localAnalyser) return
      localAnalyser.getByteFrequencyData(data)
      const average = data.reduce((total, value) => total + value, 0) / data.length
      options.inputLevel.value = Math.round(Math.min(100, (average / 90) * 100))
      options.localSpeaking.value = average > 18
    }, 180)
  }

  function stop() {
    if (vadTimer !== null) {
      window.clearInterval(vadTimer)
      vadTimer = null
    }
    options.localSpeaking.value = false
    options.inputLevel.value = 0
    localAnalyser = null
  }

  function close() {
    stop()
    void audioContext?.close()
    audioContext = null
  }

  return {
    attach,
    start,
    stop,
    close,
  }
}
