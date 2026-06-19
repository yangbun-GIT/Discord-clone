# Realtime Communication QA

Use this checklist for Stage C8 and later communication regressions. It separates
automated code-path smoke from real-device and real-network release gates.

## Automated Browser Smoke

Prerequisites:

- Backend is available at `http://127.0.0.1:8000`.
- Frontend is available at `http://127.0.0.1:5173`.
- `npm --prefix frontend install` has installed the official `playwright`
  devDependency.
- On Windows, system Chrome is available at
  `C:\Program Files\Google\Chrome\Application\chrome.exe`, or set
  `CHROME_EXECUTABLE`.

Run:

```powershell
npm run smoke:realtime:browser
```

Optional endpoints:

```powershell
$env:APP_URL = "http://127.0.0.1:5173"
$env:REST_BASE = "http://127.0.0.1:8000"
$env:CHROME_EXECUTABLE = "C:/Program Files/Google/Chrome/Application/chrome.exe"
npm run smoke:realtime:browser
```

The script creates temporary local dev users, a temporary shared guild, an invite,
and a DM. It verifies:

- Server text message appears in a second browser context through gateway dispatch.
- DM message appears in a second browser context through gateway dispatch.
- Two users join the same voice channel with fake microphone devices.
- Remote audio sink appears.
- Voice peer count appears in the voice panel.
- Mute/deafen controls toggle.
- Fake screen-share path becomes visible.

Privacy rules:

- The script must not print JWTs, message bodies, ICE candidates, TURN credentials,
  media device labels, or DM contents.
- Fake-device success is not a real microphone quality pass.
- Fake screen-share success is not a real screen picker UX pass.

Latest C8 automated result:

- Date: 2026-06-19.
- Command: `npm run smoke:realtime:browser`.
- Result: passed for two-context server text realtime, DM realtime, voice remote
  audio sink, peer detail visibility, mute/deafen toggles, fake screen-share
  visibility, and zero browser errors.
- Scope: same-PC automated fake-device code-path coverage only. It is not a LAN,
  TURN/NAT, real microphone quality, or real screen-picker release gate.

## Manual Same-PC QA

1. Open two isolated browser profiles.
2. Sign in as two different users.
3. Create or join one shared server.
4. Send one server text message from user A and confirm user B sees it without
   refresh.
5. Open a DM between the two users.
6. Send one DM from user A and confirm user B sees it without refresh.
7. Join the same voice channel from both sessions.
8. Confirm each session shows the other participant.
9. Confirm peer count reaches one connected peer.
10. Toggle mute and deafen.
11. Start and stop real screen sharing.
12. Refresh one session and confirm REST reload plus gateway reconnect recovers
    text/DM state.

## LAN QA

Follow `docs/voice-qa.md#lan-smoke-test`. Record:

- Host IP.
- Frontend URL.
- Backend health URL.
- Whether `/gateway` stays connected.
- Whether text, DM, and voice participant state work from another device.

LAN success is not TURN/NAT internet success.

## TURN/NAT QA

Follow `docs/voice-qa.md#turn--nat-test`. Record:

- ICE server count.
- `turn_configured` value.
- Networks used.
- Browser media permission result.
- Voice peer stability.
- Screen-share result.

Do not mark internet voice complete unless TURN is configured and a real
different-network test passes.
