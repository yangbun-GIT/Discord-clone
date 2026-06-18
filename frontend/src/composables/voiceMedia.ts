export async function captureMicrophone() {
  return navigator.mediaDevices.getUserMedia({
    audio: {
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true,
    },
    video: false,
  })
}

export async function captureDisplay() {
  return navigator.mediaDevices.getDisplayMedia({
    video: {
      frameRate: { ideal: 15, max: 30 },
      width: { ideal: 1280 },
      height: { ideal: 720 },
    },
    audio: false,
  })
}

export function stopMediaStream(stream: MediaStream | null) {
  stream?.getTracks().forEach((track) => track.stop())
}

export function setAudioTracksMuted(stream: MediaStream | null, muted: boolean) {
  stream?.getAudioTracks().forEach((track) => {
    track.enabled = !muted
  })
}

export function screenTrackIsActive(stream: MediaStream) {
  return stream.getVideoTracks().some((track) => track.readyState === 'live')
}
