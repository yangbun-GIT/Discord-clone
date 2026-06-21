# Discord Clone

Zero-budget Discord clone based on the SRS provided for the project.

## 프로젝트 적용 및 실행 방법

이 프로젝트는 Discord 클론 코딩 과제용으로 작성된 Front-End + Back-End 통합 프로젝트입니다. 기본 실행 방식은 상시 서버 배포가 아니라 **로컬 Docker Compose 실행**이며, 필요할 때만 Cloudflare Tunnel로 임시 HTTPS 외부 접속 주소를 만들어 시연할 수 있습니다.

### 1. 준비물

- Git
- Docker Desktop
- Node.js 및 npm
- PowerShell

Docker Desktop은 실행된 상태여야 하며, 처음 실행하는 경우 이미지 빌드 때문에 시간이 조금 걸릴 수 있습니다.

### 2. 프로젝트 내려받기

```powershell
git clone https://github.com/yangbun-GIT/Discord-clone.git
cd Discord-clone
```

이미 프로젝트 폴더가 있다면 해당 폴더에서 최신 내용을 받은 뒤 진행합니다.

```powershell
git pull origin main
```

### 3. 기본 로컬 실행

아래 명령은 프론트엔드, 백엔드, PostgreSQL, Redis, WebSocket gateway, 음성 상태 메타데이터 구성을 함께 실행합니다.

```powershell
npm run docker:up
```

실행 후 브라우저에서 아래 주소로 접속합니다.

- 앱: `http://127.0.0.1:5173`
- 백엔드 상태 확인: `http://127.0.0.1:8000/api/health`

처음 접속하면 회원가입 화면에서 테스트 계정을 직접 생성해 사용할 수 있습니다. 두 브라우저 세션 또는 두 기기에서 서로 다른 계정을 만들면 친구 추가, DM, 서버 메시지, 음성 채널, 화면 공유 흐름을 확인할 수 있습니다.

### 4. 마이크와 화면 공유까지 확인하는 HTTPS 실행

브라우저는 `localhost`가 아닌 일반 HTTP 주소에서 마이크와 화면 공유를 제한합니다. 같은 PC에서 마이크와 화면 공유를 안정적으로 확인하려면 HTTPS Docker 구성을 사용합니다.

```powershell
npm run docker:up:https:detached
```

실행 후 아래 주소로 접속합니다.

- 앱: `https://localhost:5173`
- 백엔드 상태 확인: `https://localhost:5173/api/health`

같은 Wi-Fi의 다른 PC에서 접속하려면 개발 인증서가 필요합니다. 자세한 절차는 `docs/assignment-submission-guide.md`와 `docs/deployment.md`를 참고합니다.

### 5. 선택 사항: Cloudflare Tunnel로 임시 외부 접속

상시 public VM/VPS 배포 없이 외부 네트워크에서 임시로 접속 테스트를 해야 한다면 Cloudflare Quick Tunnel을 사용할 수 있습니다. 이 방식은 정식 배포가 아니라 로컬 실행 앱을 임시 HTTPS 주소로 노출하는 시연 경로입니다.

먼저 HTTPS Docker stack과 tunnel 전용 프론트 컨테이너를 실행합니다.

```powershell
npm run docker:up:https:detached
npm run docker:up:cloudflare-tunnel
```

그 다음 Cloudflare 공식 `cloudflared`가 설치되어 있다면 아래 명령을 실행합니다.

```powershell
cloudflared tunnel --url http://localhost:5174
```

터미널에 출력되는 `https://*.trycloudflare.com` 주소로 외부 기기에서 접속할 수 있습니다. 이 주소는 매번 바뀌는 임시 주소이며 README나 문서에 영구 배포 주소처럼 기록하면 안 됩니다.

주의할 점:

- Cloudflare Tunnel은 HTTPS/WSS 접속 확인에는 유용합니다.
- TURN 서버가 기본 설정되어 있지 않으므로 모든 NAT/방화벽 환경에서 음성/화면 공유가 항상 성공한다고 보장하지 않습니다.
- GitHub Pages 같은 정적 배포만으로는 백엔드, WebSocket, DB, 음성 통신 구성을 모두 실행할 수 없습니다.

### 6. 주요 기능 확인 순서

1. 회원가입 또는 로그인
2. 서버 생성
3. 초대 코드 생성 및 참여
4. 친구 추가와 친구 요청 수락
5. DM 송수신
6. 서버 텍스트 채널 메시지 송수신
7. 음성 채널 참여
8. 마이크 음소거와 소리 차단 독립 동작 확인
9. 화면 공유 시작과 중지
10. 음성 및 비디오 설정 확인

### 7. 검증 명령

로컬 제출용 실행 상태를 자동으로 점검하려면 아래 명령을 사용합니다.

```powershell
npm run check:submission:local
```

HTTPS 로컬 통신 smoke test가 필요하면 HTTPS stack 실행 후 아래 명령을 사용합니다.

```powershell
npm run smoke:realtime:browser:https
```

전체 개발 검증 후보는 아래 명령들입니다.

```powershell
npm run test:frontend
npm run test:backend
npm run lint:backend
npm run lint:frontend
npm --prefix frontend run build
```

### 8. 종료 및 초기화

컨테이너를 종료하려면 아래 명령을 사용합니다.

```powershell
npm run docker:down
```

이 명령은 PostgreSQL Docker volume을 보존합니다. 로컬 테스트 데이터를 모두 지우고 처음 상태로 되돌리려면 아래 명령을 사용합니다.

```powershell
docker compose down -v
```

### 9. 관련 문서

- 과제 제출/시연 가이드: `docs/assignment-submission-guide.md`
- 배포 및 Cloudflare Tunnel 안내: `docs/deployment.md`
- 음성 QA 기록: `docs/voice-qa.md`
- 실시간 통신 QA 기록: `docs/realtime-communication-qa.md`
- 프로젝트 구조 지도: `docs/project-file-map.md`

### 10. GitHub 제출 파일 정리 기준

GitHub에는 프로젝트 실행, 빌드, 검증에 필요한 소스와 Markdown 문서만 올립니다.
로컬 QA 캡처, OBS 영상, 실제 Discord 참고 이미지, 개발 인증서, 개인 환경 파일은
제출 저장소에 포함하지 않습니다.

- 로컬 인증서: `certs/` 아래의 실제 인증서 파일은 무시됩니다.
- 로컬 QA 이미지: `docs/qa-artifacts/`의 생성 PNG는 무시됩니다.
- 실제 Discord/클론 참고 캡처: `docs/reference-screenshots/` 하위 캡처는 무시됩니다.
- 통화/화면공유 테스트 영상: `docs/reference-videos/` 하위 영상과 `*.mp4` 등 영상 파일은 무시됩니다.
- 원본 명세서나 개인 문서: `*.docx`, `*.pdf`, `*.pptx`, `*.xlsx`는 기본적으로 무시됩니다.

필요한 실행 예시는 `.env.example`, `deploy/production.env.example`처럼 예시 파일로만
관리하고, 실제 비밀값은 `.env` 또는 로컬 환경에만 둡니다.

## Stack

- Backend: Python 3.14, FastAPI, asyncpg, Redis asyncio client, Pydantic v2
- Frontend: Vue 3, Vite, Pinia, Vue Router, Oxlint
- Realtime: Discord-style gateway opcodes over WebSocket
- Data model: PostgreSQL schema with JavaScript-safe Snowflake IDs and bitfield permissions

## Assignment Submission Quick Start

The default assignment submission path is local Docker Compose, not an always-on
public VM deployment. This runs the frontend, backend, PostgreSQL, WebSocket
gateway, and voice metadata locally so a grader can confirm that the project
contains both frontend and backend implementation.

Run the full stack:

```powershell
npm run docker:up
```

Open:

- App: `http://127.0.0.1:5173`
- Backend health: `http://127.0.0.1:8000/api/health`

Check the local submission stack:

```powershell
npm run check:submission:local
```

This automatically detects the normal HTTP Docker stack or the HTTPS LAN Docker
stack and verifies the frontend, same-origin backend health, PostgreSQL-backed
health metadata, voice readiness metadata, and `/gateway` HELLO.

Create two local accounts from the Register screen to test Friends, DM, server
messages, voice channels, and screen sharing. Use the Demo user button only for
quick seeded workspace exploration.

Stop the stack:

```powershell
npm run docker:down
```

For same-Wi-Fi two-PC microphone/screen-share tests, use the Docker HTTPS LAN path
below. For temporary external access without a permanent VM, run the local stack and
expose the HMR-free tunnel frontend with Cloudflare Tunnel:

```powershell
npm run docker:up:https:detached
npm run docker:up:cloudflare-tunnel
cloudflared tunnel --url http://localhost:5174
```

Cloudflare Tunnel is an optional demo path that creates a temporary HTTPS public
URL to the local app. It is not a formal deployment, and WebRTC media across
different networks still needs a TURN server for reliable voice/screen sharing.
The full submission/demo guide is `docs/assignment-submission-guide.md`.

## Local Setup

Install frontend dependencies:

```powershell
npm --prefix frontend install
```

Install backend dependencies:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python -m pip install -e .\backend[dev]
```

Run the backend:

```powershell
npm run dev:backend
```

Run the frontend in another terminal:

```powershell
npm run dev:frontend
```

Open `http://127.0.0.1:5173`.

For same-LAN testing from another PC or mobile device, bind both dev servers to all
interfaces:

```powershell
npm run dev:backend:lan
npm run dev:frontend:lan
```

Find the host IPv4 address with `ipconfig`, then open
`http://<host-ip>:5173` from the second device. If you bypass the Vite proxy and call
the backend directly from the browser, add `http://<host-ip>:5173` to
`CORS_ORIGINS`. Windows firewall must allow ports `5173` and `8000`.

Browser microphone and screen-capture APIs treat `localhost` as secure, but they
usually block `http://<host-ip>` LAN origins. For same-LAN media testing, use a
locally trusted development certificate and run the HTTPS LAN frontend:

```powershell
$env:VITE_HTTPS_KEY_FILE="C:\path\to\host-ip-key.pem"
$env:VITE_HTTPS_CERT_FILE="C:\path\to\host-ip-cert.pem"
$env:VITE_BACKEND_PROXY_TARGET="http://127.0.0.1:8000"
npm run dev:backend:lan
npm run dev:frontend:lan:https
```

Then open `https://<host-ip>:5173` from the second device. The certificate must be
trusted on that device, and the certificate subject/SAN must match the host name or
IP used in the browser. Do not commit local certificate keys.

The frontend starts at the login/register screen when no saved session exists. Use
the Demo user button for the seeded local workspace.

## Docker Setup

Docker is optional for day-to-day development, but useful for onboarding, reproducible
runtime checks, and future VM deployment. The Compose stack includes local PostgreSQL
for persistence.

Run the full stack with Compose:

```powershell
npm run docker:up
```

Stop containers:

```powershell
npm run docker:down
```

`npm run docker:down` preserves the PostgreSQL volume. To reset local Docker data,
run `docker compose down -v`.

Docker exposes the same local URLs:

- Frontend: `http://127.0.0.1:5173`
- Backend health: `http://127.0.0.1:8000/api/health`

For Docker LAN access, open `http://<host-ip>:5173`; Compose already publishes
ports `5173` and `8000` on the host.

For Docker LAN media testing from another PC, HTTP is not enough because browsers
block microphone and screen capture on non-localhost insecure origins. Generate a
local development certificate for the host IP, trust the exported root CA `.cer`
file on the second device, and run the HTTPS Compose override:

```powershell
.\scripts\create_lan_https_cert.ps1 -HostName <host-ip>
npm run docker:up:https:detached
```

Then open `https://<host-ip>:5173` from the notebook. The frontend remains
same-origin for `/api` and `/gateway`; Vite terminates HTTPS and proxies to the
backend container over the internal Docker network. Docker HTTPS uses
`certs/lan-dev.pfx`; generated files under `certs/` are ignored by Git and must
not be committed. When installing `certs/lan-dev-root-ca.cer` on the notebook,
compare the Windows warning thumbprint with the script's `Root CA thumbprint`
before accepting.

Useful backend auth endpoints:

- `POST http://127.0.0.1:8000/api/auth/register`
- `POST http://127.0.0.1:8000/api/auth/login`
- `GET http://127.0.0.1:8000/api/auth/me`
- `GET http://127.0.0.1:8000/api/users/me/relationships`
- `GET http://127.0.0.1:8000/api/dms`
- `GET http://127.0.0.1:8000/api/store/catalog`
- `GET http://127.0.0.1:8000/api/store/items/6401`

Authenticated users can create a server from the `Create server` button. New servers
start with `general` and `voice-room` channels.

Server owners can create invite codes from the top bar. Other authenticated users can
join with those codes from `Join server`.

## Environment

Copy `.env.example` to `.env` and fill values as external services become available.
Native local development works without `DATABASE_URL` or `REDIS_URL`; it uses an
in-memory demo store while preserving the async connection-pool boundaries required
by the SRS. Docker Compose supplies its own local PostgreSQL URL automatically.

Messages, channels, relationships, and direct messages created in Docker mode persist
in the local PostgreSQL volume. Messages, channels, and direct messages created in
native demo mode are kept in the running backend process and reset when that process
restarts.

WebRTC voice uses `WEBRTC_ICE_SERVERS_JSON` from the backend environment. The default
STUN server is enough for local development; deployed voice should use a TURN provider
such as Open Relay or Metered Video.
Voice controls support microphone mute, input/output device preferences, optional
free RNNoise client-side denoising, combined input-level/sensitivity feedback, and
screen sharing.
Screen sharing uses the browser display-capture permission prompt and works only while
connected to a voice channel.
The backend voice metadata also reports whether TURN is configured, and the voice
panel shows peer count, RTT, jitter, packet loss, and outbound bitrate while connected.
For a credential-safe readiness check before external testing, run:

```powershell
npm run check:voice:readiness
```

This calls `/api/meta/voice/readiness` and prints only ICE server count plus
STUN/TURN readiness. It does not print ICE URLs, TURN credentials, tokens, or media
device labels.

LAN success and TURN/NAT internet success are separate release gates. Do not mark
internet voice complete unless the readiness check reports `turn_configured: true`
and two users on different networks can complete a real voice/screen-share test.

Assignment submission and demo steps are maintained in
`docs/assignment-submission-guide.md`. Deployment notes are maintained in
`docs/deployment.md`. Voice QA steps are maintained in `docs/voice-qa.md`, and
communication QA steps are maintained in
`docs/realtime-communication-qa.md`. The documentation index is maintained in
`docs/README.md`.
Git workflow notes are maintained in `docs/GITHUB_COLLABORATION_WORKFLOW.md`, and
prompt-alignment status is maintained in `docs/PROMPT_COMPLIANCE.md`.
The current Discord app clone roadmap is maintained in
`docs/discord-app-clone-implementation-plan.md`. The deferred Store-like shop roadmap
is maintained in `docs/store-clone-implementation-plan.md`.

## Verification

```powershell
npm run test:frontend
npm run test:backend
npm run lint:backend
npm run lint:frontend
npm --prefix frontend run build
npm run check:submission:local
npm run smoke:realtime:browser
npm run smoke:realtime:browser:https
npm run smoke:realtime:redis
npm run check:deployment:readiness
docker compose exec -T backend pytest
```

`npm run smoke:realtime:browser` expects the backend at `http://127.0.0.1:8000`
and the frontend at `http://127.0.0.1:5173`. It is a same-PC fake-device smoke for
server text, DM, voice peer, remote screen-share rendering, and voice leave cleanup
code paths, not a LAN/TURN release gate. When the Docker HTTPS LAN stack is running,
use `npm run smoke:realtime:browser:https`; HTTP URLs on port `5173` will return an
empty response because Vite is serving HTTPS only. `npm run smoke:realtime:redis` expects the
primary backend at `http://127.0.0.1:8000` and a secondary backend at
`http://127.0.0.1:8001`.

As of the 2026-06-19 Stage C9 gate, the local command suite and Docker/local
communication smoke pass. Real microphone quality, real screen picker UX,
different-PC LAN, and TURN/NAT internet voice remain separate manual gates.

## External Deployment Readiness

The default assignment path is local Docker Compose plus optional Cloudflare Tunnel
for temporary external access. The VM/VPS path below is a future always-on
deployment option, not a requirement for the current submission.

The project cannot be completed for external voice through GitHub Pages or another
static-only host. The Vue bundle can be static, but the clone also needs FastAPI,
PostgreSQL, Redis fan-out, `/gateway` WebSocket upgrade, HTTPS/WSS, and TURN.

Use these reference files for a first single-server external QA deployment:

- `compose.production.example.yaml`
- `deploy/Caddyfile.example`
- `deploy/coturn/turnserver.conf.example`
- `deploy/production.env.example`
- `docs/external-deployment-runbook.md`

Before starting a VM stack, render the placeholder Compose config locally:

```powershell
npm run check:deployment:config
```

After deploying behind HTTPS, run:

```powershell
$env:DEPLOYMENT_ORIGIN = "https://<domain>"
$env:REQUIRE_TURN = "1"
npm run check:deployment:readiness
```

This verifies `/api/health`, safe voice readiness, and `/gateway` WSS HELLO without
printing credentials. A passing readiness check is still not enough by itself:
internet voice is complete only after two users on different networks can complete
voice and screen-share QA with `turn_configured: true`.
