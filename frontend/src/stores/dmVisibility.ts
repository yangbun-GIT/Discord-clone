import type { DirectMessage, DmMessage, Friend } from '../types'
import { isVisualTestMessage, isVisualTestName } from '../utils/visualNoise'

export function isVisibleDmMessage(message: DmMessage) {
  return !isVisualTestMessage(message.content) && !isVisualTestName(message.author_name)
}

export function cleanVisibleRelationships(nextRelationships: Friend[]) {
  return nextRelationships.filter(
    (friend) =>
      !isVisualTestName(friend.username)
      && !isVisualTestName(friend.handle)
      && !isVisualTestMessage(friend.activity),
  )
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
  return nextDms.flatMap((dm) => {
    const clean = cleanVisibleDirectMessage(dm)
    return clean ? [clean] : []
  })
}
