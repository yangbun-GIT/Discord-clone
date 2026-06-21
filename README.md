# Discord Clone

Discord의 핵심 사용 흐름을 구현한 Front-End + Back-End 통합 클론 코딩 프로젝트입니다.

과제 제출 기준의 기본 실행 방식은 **로컬 Docker Compose 실행**입니다. 별도 public 서버 배포 없이 채점자가 로컬에서 프론트엔드, 백엔드, 데이터베이스, WebSocket gateway를 함께 실행해 확인할 수 있도록 구성했습니다. 필요하면 Cloudflare Tunnel을 사용해 임시 HTTPS 외부 접속 주소로 시연할 수 있습니다.

## 기술 스택

- Front-End: Vue 3, Vite, Pinia, Vue Router
- Back-End: FastAPI, Pydantic, asyncpg
- Database: PostgreSQL
- Realtime: WebSocket gateway
- Voice/Screen Share: WebRTC P2P, STUN, 선택적 TURN 확장 구조
- Runtime: Docker Compose

## 준비물

- Git
- Docker Desktop
- Node.js 및 npm
- PowerShell
- Chrome, Edge, Whale 등 최신 Chromium 계열 브라우저 권장

Docker Desktop은 실행된 상태여야 합니다. 최초 실행 시 이미지 빌드 때문에 시간이 걸릴 수 있습니다.

## 프로젝트 내려받기

```powershell
git clone https://github.com/yangbun-GIT/Discord-clone.git
cd Discord-clone
```

이미 프로젝트 폴더가 있다면 최신 내용을 받은 뒤 실행합니다.

```powershell
git pull origin main
```

## 기본 실행

아래 명령은 프론트엔드, 백엔드, PostgreSQL, Redis, WebSocket gateway, 음성 상태 메타데이터 구성을 함께 실행합니다.

```powershell
npm run docker:up
```

접속 주소:

- 앱: `http://127.0.0.1:5173`
- 백엔드 상태 확인: `http://127.0.0.1:8000/api/health`

처음 접속하면 회원가입 화면에서 계정을 생성해 사용할 수 있습니다. 두 브라우저 세션 또는 두 기기에서 서로 다른 계정을 만들면 친구 추가, DM, 서버 메시지, 음성 채널 흐름을 확인할 수 있습니다.

## 마이크와 화면 공유 확인용 HTTPS 실행

브라우저는 `localhost`가 아닌 일반 HTTP 주소에서 마이크와 화면 공유를 제한합니다. 같은 PC에서 마이크와 화면 공유까지 확인하려면 HTTPS 구성을 사용합니다.

```powershell
npm run docker:up:https:detached
```

접속 주소:

- 앱: `https://localhost:5173`
- 백엔드 상태 확인: `https://localhost:5173/api/health`

브라우저에서 로컬 개발 인증서 경고가 보일 수 있습니다. 같은 PC의 `localhost` 검증 용도라면 브라우저 안내에 따라 진행하면 됩니다.

## 같은 Wi-Fi의 다른 PC에서 확인

같은 Wi-Fi 또는 같은 공유기 아래의 다른 PC에서 마이크와 화면 공유를 확인하려면 HTTPS secure context가 필요합니다.

1. 호스트 PC에서 IPv4 주소를 확인합니다.

```powershell
ipconfig
```

2. 호스트 IP용 개발 인증서를 생성합니다.

```powershell
.\scripts\create_lan_https_cert.ps1 -HostName <host-ip>
```

3. HTTPS Docker stack을 실행합니다.

```powershell
npm run docker:up:https:detached
```

4. 다른 PC에서 `https://<host-ip>:5173`으로 접속합니다.

5. 다른 PC에는 생성된 루트 CA 인증서를 신뢰 저장소에 설치해야 합니다.

주의:

- 인증서 파일과 private key는 Git에 올리지 않습니다.
- 인증서의 대상 IP와 브라우저에 입력한 IP가 일치해야 합니다.
- Windows 방화벽에서 필요한 포트가 차단되어 있으면 접속되지 않을 수 있습니다.

## 선택 사항: Cloudflare Tunnel 임시 외부 접속

상시 public VM/VPS 배포 없이 외부 네트워크에서 임시로 접속 테스트를 해야 한다면 Cloudflare Quick Tunnel을 사용할 수 있습니다.

```powershell
npm run docker:up:https:detached
npm run docker:up:cloudflare-tunnel
cloudflared tunnel --url http://localhost:5174
```

터미널에 출력되는 `https://*.trycloudflare.com` 주소로 외부 기기에서 접속할 수 있습니다.

주의:

- 이 주소는 매번 바뀌는 임시 주소입니다.
- Cloudflare Tunnel은 정식 배포가 아니라 로컬 실행 앱을 외부에 임시 노출하는 시연 경로입니다.
- TURN 서버가 기본 설정되어 있지 않으므로 모든 NAT/방화벽 환경에서 음성/화면 공유가 항상 성공한다고 보장하지 않습니다.
- GitHub Pages 같은 정적 배포만으로는 FastAPI, PostgreSQL, WebSocket, WebRTC signaling 구성을 모두 실행할 수 없습니다.

## 주요 기능 확인 순서

1. 회원가입 또는 로그인
2. 서버 생성
3. 초대 코드 생성 및 참여
4. 친구 추가와 친구 요청 수락
5. DM 송수신
6. 서버 텍스트 채널 메시지 송수신
7. DM 개인 통화
8. 서버 음성 채널 참여
9. 마이크 음소거와 소리 차단 독립 동작 확인
10. 화면 공유 시작과 중지
11. 음성 및 비디오 설정 확인
12. 서버 멤버 권한 변경
13. 서버 나가기 또는 권한이 있는 경우 서버 삭제

## 구현된 주요 범위

- 계정 생성 및 로그인
- 친구 추가, 요청 수락, 친구 상태 표시
- DM 생성, DM 메시지 송수신, 메시지 삭제
- 서버 생성, 참여, 초대, 나가기, 삭제
- 텍스트 채널 메시지 송수신
- 메시지 날짜 구분선과 최신 메시지 기준 스크롤
- 서버 음성 채널
- DM 개인 통화
- 마이크 음소거와 소리 차단 분리
- 화면 공유
- 음성 입력 감도, 입력/출력 볼륨, RNNoise 잡음 제거
- 사용자 설정 화면
- 한국어/영어 UI 기반 구조

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

로컬 제출 실행 점검:

```powershell
npm run check:submission:local
```

HTTPS 실시간 통신 smoke test:

```powershell
npm run smoke:realtime:browser:https
```

## 종료 및 초기화

컨테이너 종료:

```powershell
npm run docker:down
```

로컬 Docker 데이터까지 초기화:

```powershell
docker compose down -v
```

`npm run docker:down`은 PostgreSQL volume을 보존합니다. 테스트 데이터를 모두 지우고 처음 상태로 돌리고 싶을 때만 `docker compose down -v`를 사용합니다.

## 환경 변수와 보안

환경 변수 예시는 `.env.example`에 있습니다. 실제 `.env` 파일은 Git에 올리지 않습니다.

Git에 올리지 않는 항목:

- 실제 `.env`
- 데이터베이스 비밀번호
- JWT secret
- TURN credential
- Cloudflare token
- 개발 인증서와 private key
- 로컬 테스트 캡처 이미지
- OBS 녹화 영상
- 원본 명세서 문서
- 작업 과정 추적용 문서

GitHub에는 프로젝트 실행, 빌드, 검증에 필요한 소스와 이 `README.md`만 남기는 것을 기준으로 정리했습니다.

## 제한 사항

- Cloudflare Tunnel은 임시 외부 접속 시연 경로이며 정식 상시 배포가 아닙니다.
- TURN 서버가 기본 설정되어 있지 않으므로 모든 외부 네트워크 조합에서 음성/화면 공유 성공을 보장하지 않습니다.
- 실제 마이크 품질, 블루투스 헤드셋 호환성, 화면 공유 권한 동작은 브라우저와 OS 환경의 영향을 받습니다.
- 화면 공유 권한을 취소한 경우 브라우저 권한 정책에 따라 다시 권한을 요청해야 합니다.
