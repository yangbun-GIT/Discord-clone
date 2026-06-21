# Discord Clone

Discord의 핵심 사용 흐름을 Front-End와 Back-End까지 포함해 구현한 클론 코딩 프로젝트입니다.
정적 화면만 제공하는 앱이 아니라 FastAPI 백엔드, PostgreSQL, WebSocket gateway, WebRTC 음성/화면 공유를 함께 실행하는 통합 웹 애플리케이션입니다.

과제 제출 기준의 기본 실행 방식은 **로컬 Docker Compose 실행**입니다. 필요하면 Cloudflare Quick Tunnel을 사용해 로컬 앱을 임시 HTTPS 주소로 외부 네트워크에 공개해 시연할 수 있습니다.

## 기술 스택

- Front-End: Vue 3, Vite, TypeScript, Pinia
- Back-End: FastAPI, Pydantic, async SQLAlchemy/asyncpg
- Database: PostgreSQL
- Realtime: WebSocket gateway
- Voice/Screen Share: WebRTC P2P, STUN, TURN 확장 준비
- Runtime: Docker Compose
- Optional external demo: Cloudflare Quick Tunnel

## Front-End와 Back-End 포함 범위

이 프로젝트는 프론트엔드 단독 정적 페이지가 아니라, 화면 조작과 서버 상태가 실제 백엔드 API와 실시간 통신 계층에 연결된 구조입니다.

- 프론트엔드는 Discord와 유사한 앱 레이아웃, 친구/DM/서버/채널/음성/설정 화면, WebRTC 미디어 제어 UI를 담당합니다.
- 백엔드는 인증, 친구 관계, 서버와 채널, 메시지 저장, 권한, 초대 코드, WebSocket gateway, 음성 채널 상태와 signaling 중계를 담당합니다.
- PostgreSQL은 사용자, 친구, 서버, 채널, 메시지, 멤버십 같은 지속 데이터를 저장합니다.
- WebSocket gateway는 메시지/상태/음성 signaling 이벤트를 여러 브라우저 세션에 실시간으로 전달합니다.
- WebRTC는 브라우저 간 음성 통화와 화면 공유 미디어 연결을 담당합니다.

## 프로젝트 구조

```text
Discord-clone/
├─ backend/                         # FastAPI ASGI 백엔드
│  ├─ app/main.py                    # 앱 진입점, lifespan, 라우터 등록
│  ├─ app/api/routes/                # REST API 라우트
│  ├─ app/gateway/                   # Discord-style WebSocket gateway
│  ├─ app/models/                    # DB 모델
│  ├─ app/repositories/              # PostgreSQL 저장소 계층
│  ├─ app/services/                  # 도메인 서비스
│  └─ tests/                         # 백엔드 테스트
├─ frontend/                         # Vue 3 + Vite 프론트엔드
│  ├─ src/App.vue                    # 앱 쉘
│  ├─ src/components/                # 주요 UI 컴포넌트
│  ├─ src/composables/               # gateway, voice, WebRTC 조합 로직
│  ├─ src/stores/                    # Pinia 전역 상태
│  ├─ src/api/                       # REST API 클라이언트
│  ├─ src/i18n/                      # 한국어/영어 UI 문자열
│  └─ src/styles/                    # 전역 스타일
├─ scripts/                          # 실행/검증 보조 스크립트
├─ deploy/                           # 배포 예시 설정
├─ compose.yaml                      # 기본 Docker Compose
├─ compose.https.yaml                # HTTPS 로컬 실행 오버레이
├─ compose.cloudflare-tunnel.yaml    # Cloudflare 정적 터널용 오버레이
├─ .env.example                      # 환경변수 예시
├─ package.json                      # 루트 실행 명령
└─ README.md                         # 실행 및 제출 안내
```

## 통신 구현

이 프로젝트의 핵심은 실제 브라우저 세션 간 통신입니다. 통신은 REST API, WebSocket gateway, WebRTC가 역할을 나눠 처리합니다.

### 1. REST API

REST API는 저장이 필요한 데이터의 기준점입니다.

- 로그인/회원가입
- 친구 요청과 친구 관계
- 서버, 채널, 초대 코드
- DM과 서버 텍스트 메시지 저장
- 서버 멤버와 권한

메시지 본문과 관계 데이터는 백엔드 API를 통해 PostgreSQL에 저장되고, 프론트엔드는 저장 성공 이후 gateway 이벤트를 통해 다른 세션에 변경 사항을 전달받습니다.

### 2. WebSocket Gateway

WebSocket gateway는 Discord와 유사한 `op`, `d`, `s`, `t` payload 구조를 사용합니다.

- `IDENTIFY`: 클라이언트 세션 식별
- `HEARTBEAT`: 연결 유지
- `READY`: 초기 gateway 준비 상태
- Dispatch event: 메시지 생성/삭제, 친구 요청, 상태 변경, 음성 상태 변경, WebRTC signaling 등

Gateway는 실시간 알림과 세션 간 동기화를 담당합니다. 텍스트/DM의 source of truth는 REST 저장소이고, gateway는 실시간 반영을 위한 notification 계층으로 동작합니다.

### 3. WebRTC 음성/화면 공유

음성 채널과 DM 통화는 브라우저 WebRTC P2P 연결을 사용합니다.

- Gateway가 offer/answer/ICE candidate signaling을 중계합니다.
- 미디어 스트림은 가능한 경우 브라우저 간 P2P로 직접 전달됩니다.
- 기본 ICE 서버는 STUN입니다.
- 외부 NAT/방화벽 환경에서 안정성을 높이려면 TURN 서버 설정이 필요합니다.
- 화면 공유는 브라우저의 `getDisplayMedia` 권한 흐름을 사용합니다.

현재 구현은 로컬, 같은 Wi-Fi LAN, 특정 Cloudflare Tunnel + STUN 기반 외부망 환경에서 검증되었습니다. 모든 외부 NAT 조합을 보장하려면 TURN 설정 후 별도 수동 QA가 필요합니다.

### 4. Cloudflare Tunnel 역할

Cloudflare Quick Tunnel은 로컬 앱을 임시 HTTPS 주소로 노출하는 시연 경로입니다.

- HTTPS secure context를 제공해 마이크/화면 공유 권한 테스트가 가능합니다.
- WebSocket은 WSS 경로로 프록시됩니다.
- Cloudflare Tunnel 자체가 TURN 서버 역할을 하지는 않습니다.
- 임시 URL은 매번 바뀌며 정식 배포 주소가 아닙니다.

## 실행 준비

필수 도구:

- Git
- Docker Desktop
- Node.js와 npm
- PowerShell
- Chrome, Edge, Whale 등 최신 Chromium 계열 브라우저 권장

Docker Desktop이 실행 중이어야 합니다. 최초 실행 시 Docker 이미지 빌드 때문에 시간이 걸릴 수 있습니다.

프로젝트 받기:

```powershell
git clone https://github.com/yangbun-GIT/Discord-clone.git
cd Discord-clone
```

이미 프로젝트 폴더가 있다면 최신 내용을 받습니다.

```powershell
git pull origin main
```

## 로컬 실행

기본 실행:

```powershell
npm run docker:up
```

접속 주소:

- 프론트엔드: `http://127.0.0.1:5173`
- 백엔드 상태 확인: `http://127.0.0.1:8000/api/health`

처음 접속하면 회원가입 화면에서 계정을 만들거나 개발 사용자 기능으로 테스트 계정을 생성할 수 있습니다. 두 개 이상의 브라우저 세션 또는 서로 다른 기기에서 다른 계정으로 접속하면 친구, DM, 서버 메시지, 음성 채널 흐름을 확인할 수 있습니다.

## 회원가입과 로그인

첫 사용자는 로그인 화면의 `회원가입` 탭에서 사용자명과 비밀번호를 입력해 계정을 생성합니다. 생성한 계정은 같은 사용자명과 비밀번호로 다시 로그인할 수 있습니다.

신규 계정은 처음 접속할 때 `Guide` 계정이 친구로 자동 등록되고, 다이렉트 메시지로 기본 사용 안내를 받습니다. 신규 계정에 불필요한 데모 친구, 이전 테스트 DM, 친구 요청이 자동으로 추가되지 않도록 정리되어 있습니다.

`개발 사용자` 버튼은 로컬 개발과 시연용 관리자 계정으로 바로 접속하는 기능입니다. 이 계정은 `admin` 이름을 사용하며 기본 서버의 소유자 권한을 가집니다. 일반 회원가입 흐름을 확인할 때는 `회원가입` 탭을 사용하세요.

이전에 만든 로컬 테스트 계정과 메시지를 모두 지우고 깨끗한 초기 상태로 되돌리려면 아래 초기화 명령을 사용합니다.

```powershell
docker compose down -v
npm run docker:up
```

## HTTPS 실행

마이크와 화면 공유는 브라우저의 secure context 정책 영향을 받습니다. 같은 PC에서 마이크와 화면 공유까지 확인하려면 HTTPS 실행을 권장합니다.

```powershell
npm run docker:up:https:detached
```

접속 주소:

- 앱: `https://localhost:5173`
- 상태 확인: `https://localhost:5173/api/health`

브라우저에서 로컬 개발 인증서 경고가 보일 수 있습니다. 같은 PC의 `localhost` 검증 용도라면 브라우저 안내에 따라 진행하면 됩니다.

## Cloudflare Tunnel 외부 접속

외부 네트워크에서 임시로 접속해야 할 때 Cloudflare Quick Tunnel을 사용할 수 있습니다. 정식 배포가 아니라 로컬 실행 앱을 임시 HTTPS 주소로 공개하는 방식입니다.

수정사항이 Cloudflare URL에도 바로 반영되어야 하면 Vite 개발 서버에 직접 연결하는 dev 터널을 사용합니다.

```powershell
npm run docker:up:https:detached
npm run tunnel:cloudflare:dev
```

터미널에 출력되는 `https://*.trycloudflare.com` 주소로 외부 기기에서 접속합니다. 이 방식은 `https://localhost:5173`에 직접 연결되므로 로컬 수정사항이 Cloudflare URL에도 즉시 반영됩니다.

정적 빌드 결과를 확인해야 하는 경우에는 아래 방식을 사용할 수 있습니다.

```powershell
npm run docker:up:https:detached
npm run docker:up:cloudflare-tunnel
cloudflared tunnel --url http://localhost:5174
```

정적 빌드 방식은 프론트엔드 수정 후 `frontend-tunnel` 컨테이너를 다시 빌드해야 변경사항이 반영됩니다.

주의:

- Cloudflare Quick Tunnel URL은 임시 주소입니다.
- Cloudflare Tunnel은 TURN 서버가 아닙니다.
- TURN이 설정되지 않은 상태에서는 모든 외부 NAT/방화벽 환경의 음성/화면 공유 성공을 보장하지 않습니다.
- GitHub Pages 같은 정적 배포만으로는 FastAPI, PostgreSQL, WebSocket, WebRTC signaling을 함께 실행할 수 없습니다.

## 검증 명령

프론트엔드 테스트:

```powershell
npm run test:frontend
```

백엔드 테스트:

```powershell
npm run test:backend
```

Lint:

```powershell
npm run lint:frontend
npm run lint:backend
```

프론트엔드 빌드:

```powershell
npm --prefix frontend run build
```

제출용 로컬 실행 점검:

```powershell
npm run check:submission:local
```

HTTPS 실시간 통신 smoke test:

```powershell
npm run smoke:realtime:browser:https
```

## 종료와 초기화

컨테이너 종료:

```powershell
npm run docker:down
```

Docker volume까지 초기화:

```powershell
docker compose down -v
```

`npm run docker:down`은 PostgreSQL volume을 보존합니다. 테스트 데이터를 모두 지우고 처음 상태로 되돌릴 때만 `docker compose down -v`를 사용합니다.

## 주요 구현 기능

- 회원가입, 로그인, 개발 사용자 생성
- 친구 추가, 친구 요청 수락, 친구 상태 표시
- DM 생성, DM 목록, 읽지 않은 메시지 표시
- DM 메시지 송수신, 최신 메시지 기준 스크롤, 날짜 구분선, 본인 메시지 삭제
- DM 개인 통화
- 서버 생성, 서버 초대, 서버 참여, 서버 나가기, 권한이 있는 경우 서버 삭제
- 서버 rail 순서 조정, 서버 그룹화, hover/focus tooltip
- 텍스트 채널 메시지 송수신, 날짜 구분선, 사용자별 메시지 구분
- 음성 채널 참여, 참여자 목록, speaking 상태 표시
- 마이크 음소거와 소리 차단 분리
- 화면 공유 시작/중지, 다중 참여자 그리드
- 음성 장치 설정, 입력/출력 볼륨, 입력 감도, RNNoise 잡음 제거
- 사용자 설정 모달, 계정/개인정보/음성/화면/접근성/단축키/언어 설정
- 한국어/영어 UI 기반

## 환경변수와 보안

환경변수 예시는 `.env.example`에 있습니다. 실제 `.env` 파일은 Git에 올리지 않습니다.

Git에 올리지 않는 항목:

- 실제 `.env`
- 데이터베이스 비밀번호
- JWT secret
- TURN credential
- Cloudflare token
- 개발 인증서 private key
- 로컬 테스트 캡처 이미지
- OBS 녹화 영상
- 원본 명세서 문서
- 작업 과정 추적 문서

## 제한 사항

- Cloudflare Tunnel은 임시 외부 접속 시연 경로이며 정식 상시 배포가 아닙니다.
- TURN 서버가 기본 설정되어 있지 않으므로 모든 외부 네트워크 조합에서 음성/화면 공유 성공을 보장하지 않습니다.
- 실제 마이크 품질, Bluetooth 헤드셋 호환성, 화면 공유 권한 동작은 브라우저와 OS 환경에 영향을 받습니다.
- 화면 공유 권한을 취소한 경우 브라우저 정책에 따라 다시 권한을 요청해야 할 수 있습니다.
