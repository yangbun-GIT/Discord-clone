import type { DirectMessage, DmMessage, Friend } from '../types'
import { isVisualTestMessage, isVisualTestName } from '../utils/visualNoise'

export function isVisibleDmMessage(message: DmMessage) {
  return !isVisualTestMessage(message.content) && !isVisualTestName(message.author_name)
}

export function cleanVisibleRelationships(nextRelationships: Friend[]) {
  const visibleRelationships: Friend[] = []
  const seenRelationshipIds = new Set<number>()
  for (const friend of nextRelationships) {
    if (
      isVisualTestName(friend.username)
      || isVisualTestName(friend.handle)
      || isVisualTestMessage(friend.activity)
      || seenRelationshipIds.has(friend.id)
    ) {
      continue
    }
    seenRelationshipIds.add(friend.id)
    visibleRelationships.push(friend)
  }
  return visibleRelationships
}

export function cleanVisibleDirectMessage(dm: DirectMessage): DirectMessage | null {
  if (isVisualTestName(dm.display_name) || isVisualTestMessage(dm.activity)) return null
  return {
    ...dm,
    participants: dm.participants.filter(
      (participant) =>
        !isVisualTestName(participant.username)
        && !isVisualTestName(participant.handle)
        && !isVisualTestMessage(participant.activity),
    ),
    messages: dm.messages.filter(isVisibleDmMessage),
  }
}

export function cleanVisibleDirectMessages(nextDms: DirectMessage[]) {
  const visibleDms: DirectMessage[] = []
  const seenDmIds = new Set<number>()
  const seenRecipientSets = new Set<string>()
  for (const dm of nextDms) {
    const clean = cleanVisibleDirectMessage(dm)
    if (!clean || seenDmIds.has(clean.id)) continue
    const recipientKey = clean.recipient_ids.slice().sort((left, right) => left - right).join(':')
    if (seenRecipientSets.has(recipientKey)) continue
    seenDmIds.add(clean.id)
    seenRecipientSets.add(recipientKey)
    visibleDms.push(clean)
  }
  return visibleDms
}
