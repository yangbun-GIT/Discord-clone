import { createRequire } from 'node:module'
import os from 'node:os'

const require = createRequire(new URL('../frontend/package.json', import.meta.url))
const { chromium } = require('playwright')

const APP_URL = process.env.APP_URL ?? 'http://127.0.0.1:5173'
const REST_BASE = process.env.REST_BASE ?? 'http://127.0.0.1:8000'
const CHROME_EXECUTABLE =
  process.env.CHROME_EXECUTABLE
  ?? (os.platform() === 'win32'
    ? 'C:/Program Files/Google/Chrome/Application/chrome.exe'
    : undefined)

function escapeRegex(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

async function api(path, token, options = {}) {
  const response = await fetch(`${REST_BASE}${path}`, {
    ...options,
    headers: {
      'content-type': 'application/json',
      ...(token ? { authorization: `Bearer ${token}` } : {}),
      ...(options.headers ?? {}),
    },
  })
  if (!response.ok) {
    throw new Error(`${path} failed with ${response.status}`)
  }
  return await response.json()
}

async function createDevSession(username, userId) {
  return await api('/api/dev/session', null, {
    method: 'POST',
    body: JSON.stringify({ username, user_id: userId }),
  })
}

async function createPage(browser, session) {
  const context = await browser.newContext({
    permissions: ['microphone'],
    viewport: { width: 1366, height: 768 },
  })
  const page = await context.newPage()
  const events = []
  page.on('console', (message) => {
    const text = message.text()
    if (message.type() === 'error' && !text.includes('404')) {
      events.push(`console-error:${text.slice(0, 120)}`)
    }
  })
  page.on('pageerror', (error) => {
    events.push(`page-error:${error.message}`)
  })
  await page.goto(APP_URL, { waitUntil: 'networkidle', timeout: 30_000 })
  await page.evaluate((savedSession) => {
    window.localStorage.setItem('discord-clone-session', JSON.stringify(savedSession))
    window.localStorage.setItem('discord-clone-preferences', JSON.stringify({ language: 'en' }))
  }, session)
  await page.reload({ waitUntil: 'networkidle', timeout: 30_000 })
  return { context, page, events }
}

async function openGuild(page, guildName) {
  await page
    .getByRole('button', { name: new RegExp(escapeRegex(guildName), 'i') })
    .first()
    .click()
  await page.waitForTimeout(1_500)
}

async function sendComposerMessage(page, labelPattern, content) {
  const input = page.getByRole('textbox', { name: labelPattern }).last()
  await input.fill(content)
  await input.press('Enter')
}

async function waitForTextPresence(page, content, label) {
  try {
    await page.waitForFunction(
      (expected) => document.body.innerText.includes(expected),
      content,
      { timeout: 10_000 },
    )
  } catch {
    throw new Error(`${label} realtime receipt was not observed`)
  }
}

async function openDirectMessages(page) {
  await page.locator('[data-context-kind="home"]').first().click()
  await page.waitForTimeout(1_000)
}

async function openDirectMessage(page, username) {
  await page.locator('[data-context-kind="dm-row"]').filter({ hasText: username }).first().click()
  await page.waitForTimeout(1_000)
}

async function joinFirstVoiceChannel(page) {
  await page.locator('[data-context-kind="voice-channel"] .channel-button').first().click()
}

async function openVoiceWorkspace(page) {
  const voiceChat = page.getByRole('button', { name: /Open voice channel chat/i }).first()
  if (await voiceChat.isVisible().catch(() => false)) {
    await voiceChat.click()
  }
}

async function clickVoiceAction(page, label) {
  await page.getByRole('button', { name: label }).first().click()
}

async function countRemoteScreenVideos(page) {
  return await page.locator('.screen-share-tile video').evaluateAll((videos) =>
    videos.filter((video) => {
      const stream = video.srcObject
      return stream instanceof MediaStream
        && stream.getVideoTracks().some((track) => track.readyState === 'live')
    }).length,
  )
}

async function waitForRemoteScreenTile(receiverPage, senderPage) {
  try {
    await receiverPage.waitForSelector('.screen-share-tile video', {
      state: 'attached',
      timeout: 10_000,
    })
  } catch (error) {
    const receiverDebug = await receiverPage.evaluate(() => ({
      screenStages: document.querySelectorAll('.screen-share-stage').length,
      screenTiles: document.querySelectorAll('.screen-share-tile').length,
      videoElements: document.querySelectorAll('video').length,
      remoteAudioSinks: document.querySelectorAll('.voice-audio-sinks audio').length,
      remoteAudioStreams: [...document.querySelectorAll('.voice-audio-sinks audio')]
        .map((audio) => {
          const stream = audio.srcObject
          if (!(stream instanceof MediaStream)) return null
          return {
            audioTracks: stream.getAudioTracks().length,
            videoTracks: stream.getVideoTracks().map((track) => ({
              muted: track.muted,
              readyState: track.readyState,
            })),
          }
        }),
      voiceWorkspaceVisible: Boolean(document.querySelector('.voice-workspace')),
    }))
    const senderDebug = await senderPage.evaluate(() => ({
      stopShareButtons: [...document.querySelectorAll('button')]
        .filter((button) => /stop.*screen|stop.*share/i.test(button.getAttribute('aria-label') ?? button.textContent ?? ''))
        .length,
      screenTextVisible: document.body.innerText.includes('Screen sharing'),
    }))
    throw new Error(
      `remote screen tile was not observed: ${JSON.stringify({ receiverDebug, senderDebug })}`,
    )
  }
}

async function run() {
  const suffix = Date.now().toString().slice(-6)
  const userA = await createDevSession(`qaA${suffix}`, 5_100_000 + Number(suffix))
  const userB = await createDevSession(`qaB${suffix}`, 5_200_000 + Number(suffix))
  const guildName = `Realtime QA ${suffix}`

  const guild = await api('/api/guilds', userA.access_token, {
    method: 'POST',
    body: JSON.stringify({ name: guildName }),
  })
  const invite = await api(`/api/guilds/${guild.id}/invites`, userA.access_token, {
    method: 'POST',
    body: '{}',
  })
  await api(`/api/guilds/invites/${invite.code}/join`, userB.access_token, {
    method: 'POST',
    body: '{}',
  })
  await api('/api/dms', userA.access_token, {
    method: 'POST',
    body: JSON.stringify({ recipient_ids: [userB.user.id] }),
  })

  const browser = await chromium.launch({
    headless: true,
    ...(CHROME_EXECUTABLE ? { executablePath: CHROME_EXECUTABLE } : {}),
    args: [
      '--use-fake-ui-for-media-stream',
      '--use-fake-device-for-media-stream',
      '--enable-usermedia-screen-capturing',
      '--auto-select-desktop-capture-source=Entire screen',
      '--allow-http-screen-capture',
    ],
  })

  const pageA = await createPage(browser, userA)
  const pageB = await createPage(browser, userB)

  try {
    await Promise.all([
      openGuild(pageA.page, guildName),
      openGuild(pageB.page, guildName),
    ])

    const serverContent = `server-smoke-${suffix}`
    await sendComposerMessage(pageA.page, /message #?general/i, serverContent)
    await waitForTextPresence(pageB.page, serverContent, 'server message')

    await openDirectMessages(pageA.page)
    await openDirectMessages(pageB.page)
    await openDirectMessage(pageA.page, userB.user.username)
    await openDirectMessage(pageB.page, userA.user.username)

    const dmContent = `dm-smoke-${suffix}`
    await sendComposerMessage(pageA.page, new RegExp(`message ${escapeRegex(userB.user.username)}`, 'i'), dmContent)
    await waitForTextPresence(pageB.page, dmContent, 'direct message')

    await Promise.all([
      openGuild(pageA.page, guildName),
      openGuild(pageB.page, guildName),
    ])
    await joinFirstVoiceChannel(pageA.page)
    await pageA.page.waitForTimeout(1_800)
    await joinFirstVoiceChannel(pageB.page)
    await openVoiceWorkspace(pageA.page)
    await openVoiceWorkspace(pageB.page)
    await pageA.page.waitForTimeout(9_000)

    await clickVoiceAction(pageA.page, /Mute microphone/i)
    await clickVoiceAction(pageA.page, /Deafen/i)
    await clickVoiceAction(pageA.page, /^Share screen$/i)
    await pageA.page.waitForTimeout(2_500)
    await waitForRemoteScreenTile(pageB.page, pageA.page)
    const localScreenPreviewVideos = await countRemoteScreenVideos(pageA.page)

    const detailLabels = await pageA.page
      .locator('.voice-connection-card small')
      .evaluateAll((nodes) => nodes.map((node) => node.textContent ?? ''))
    const remoteAudioSinks = await pageA.page.locator('.voice-audio-sinks audio').count()
    const remoteScreenVideos = await countRemoteScreenVideos(pageB.page)
    const remoteSharingUserScreenTiles = await pageB.page.locator(`.screen-share-tile[data-user-id="${userA.user.id}"]`).count()
    const duplicateRemoteSharingParticipantCards = await pageB.page.locator(`.voice-tile.remote[data-user-id="${userA.user.id}"]`).count()
    const mutePressed = await pageA.page
      .getByRole('button', { name: /Unmute microphone|Mute microphone/i })
      .first()
      .getAttribute('aria-pressed')
    const deafenPressed = await pageA.page
      .getByRole('button', { name: /Undeafen|Deafen/i })
      .first()
      .getAttribute('aria-pressed')
    const bodyA = await pageA.page.locator('body').innerText()
    await clickVoiceAction(pageA.page, /^Stop screen share$/i)
    await pageB.page.waitForFunction(
      () => document.querySelectorAll('.screen-share-tile video').length === 0,
      null,
      { timeout: 10_000 },
    )
    const remoteScreenCleared = await pageB.page.locator('.screen-share-tile video').count() === 0
    await pageB.page.reload({ waitUntil: 'networkidle', timeout: 30_000 })
    const rejoinButton = pageB.page.getByRole('button', { name: /Rejoin voice/i }).first()
    await rejoinButton.waitFor({ state: 'visible', timeout: 10_000 })
    const voiceRejoinPromptVisible = await rejoinButton.isVisible()
    await rejoinButton.click()
    await pageA.page.waitForFunction(
      () => document.querySelectorAll('.voice-audio-sinks audio').length >= 1,
      null,
      { timeout: 15_000 },
    )
    const voiceRejoinRecovered = await pageA.page.locator('.voice-audio-sinks audio').count() >= 1
    await clickVoiceAction(pageB.page, /Disconnect voice/i)
    await pageA.page.waitForFunction(
      () => document.querySelectorAll('.voice-audio-sinks audio').length === 0,
      null,
      { timeout: 10_000 },
    )
    const voiceLeaveCleaned = await pageA.page.locator('.voice-audio-sinks audio').count() === 0

    const result = {
      serverTextRealtime: true,
      dmRealtime: true,
      voiceRemoteAudioSinks: remoteAudioSinks,
      voicePeerDetailVisible: detailLabels.some((text) => /1 peer/.test(text)),
      mutePressed: mutePressed === 'true',
      deafenPressed: deafenPressed === 'true',
      fakeScreenShareVisible: /Screen sharing/.test(bodyA),
      localScreenPreviewVideos,
      remoteScreenVideos,
      remoteSharingUserScreenTiles,
      duplicateRemoteSharingParticipantCards,
      remoteScreenCleared,
      voiceRejoinPromptVisible,
      voiceRejoinRecovered,
      voiceLeaveCleaned,
      browserErrors: [...pageA.events, ...pageB.events].length,
    }

    if (
      !result.serverTextRealtime
      || !result.dmRealtime
      || result.voiceRemoteAudioSinks < 1
      || !result.voicePeerDetailVisible
      || !result.mutePressed
      || !result.deafenPressed
      || !result.fakeScreenShareVisible
      || result.localScreenPreviewVideos < 1
      || result.remoteScreenVideos < 1
      || result.remoteSharingUserScreenTiles !== 1
      || result.duplicateRemoteSharingParticipantCards !== 0
      || !result.remoteScreenCleared
      || !result.voiceRejoinPromptVisible
      || !result.voiceRejoinRecovered
      || !result.voiceLeaveCleaned
      || result.browserErrors > 0
    ) {
      throw new Error(`browser realtime smoke failed: ${JSON.stringify(result)}`)
    }

    console.log(JSON.stringify(result))
  } finally {
    await pageA.context.close()
    await pageB.context.close()
    await browser.close()
  }
}

run().catch((error) => {
  const message = error instanceof Error ? error.message : String(error)
  console.error(message.replace(/(?:server|dm)-smoke-\d+/g, '[redacted-message]'))
  process.exit(1)
})
