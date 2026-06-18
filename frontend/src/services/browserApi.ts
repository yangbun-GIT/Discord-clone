export const browserStorage = {
  getItem(key: string): string | null {
    return globalThis.localStorage?.getItem(key) ?? null
  },
  setItem(key: string, value: string): void {
    globalThis.localStorage?.setItem(key, value)
  },
  removeItem(key: string): void {
    globalThis.localStorage?.removeItem(key)
  },
}

export async function writeClipboardText(value: string): Promise<void> {
  const writeText = globalThis.navigator?.clipboard?.writeText
  if (!writeText) throw new Error('Clipboard unavailable')
  await writeText.call(globalThis.navigator.clipboard, value)
}

export function getViewportSize(): { width: number; height: number } {
  return {
    width: globalThis.window?.innerWidth ?? 0,
    height: globalThis.window?.innerHeight ?? 0,
  }
}

export function getCurrentHref(): string {
  return globalThis.window?.location.href ?? ''
}

export function getWebSocketUrl(path: string): string {
  const location = globalThis.window?.location
  const protocol = location?.protocol === 'https:' ? 'wss' : 'ws'
  const host = location?.host ?? '127.0.0.1:8000'
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${protocol}://${host}${normalizedPath}`
}

export function getNavigatorPlatform(): string {
  return globalThis.navigator?.platform ?? 'unknown'
}

export function addDocumentEventListener<K extends keyof DocumentEventMap>(
  type: K,
  listener: (this: Document, event: DocumentEventMap[K]) => void,
  options?: boolean | AddEventListenerOptions,
): () => void {
  globalThis.document?.addEventListener(type, listener, options)
  return () => globalThis.document?.removeEventListener(type, listener, options)
}

export function runDocumentViewTransition(callback: () => void): void {
  const documentRef = globalThis.document
  const startViewTransition = documentRef?.startViewTransition
  if (!documentRef || !startViewTransition) {
    callback()
    return
  }
  startViewTransition.call(documentRef, callback)
}
