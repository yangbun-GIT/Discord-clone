const TEST_NAME_PATTERNS = [
  /\bqa\s*smoke\b/i,
  /\bstage\s*-?\s*\d+/i,
  /\bsmoke[-_\s]?test\b/i,
  /\bpersist[-_\s]?smoke\b/i,
  /\bowner[-_\s]?perm[-_\s]?smoke\b/i,
  /\blive[-_\s]?channel\b/i,
  /\btest[-_\s]?(guild|server|channel|room)\b/i,
  /\b\d{10,}\b/,
]

const TEST_MESSAGE_PATTERNS = [
  /^투표:\s*선택지를\s*입력하세요/i,
  /^poll:\s*add options/i,
  /\bchecking api logs\b/i,
  /\bstage\s*-?\s*\d+/i,
  /\bsmoke[-_\s]?test\b/i,
]

export function isVisualTestName(value: string | null | undefined) {
  const text = value?.trim()
  if (!text) return false
  return TEST_NAME_PATTERNS.some((pattern) => pattern.test(text))
}

export function isVisualTestMessage(value: string | null | undefined) {
  const text = value?.trim()
  if (!text) return false
  return TEST_MESSAGE_PATTERNS.some((pattern) => pattern.test(text))
}
