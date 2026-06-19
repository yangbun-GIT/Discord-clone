# 수동 QA 후속 수정 진행 요약 - 2026-06-19

이 문서는 `docs/remediation-tasks/manual-qa-followup-2026-06-19.md`를 기준으로
실제로 수정 진행한 내용을 한국어로 정리한 요약본이다. 원문 문서는 세부 Stage
계획과 검증 로그를 유지하고, 이 문서는 이후 작업자가 빠르게 현재 상태를
파악하기 위한 한국어 확인용 문서로 사용한다.

## 기준 문서

- 원문: `docs/remediation-tasks/manual-qa-followup-2026-06-19.md`
- 범위: Stage M1부터 M10까지
- 목적: 수동 QA에서 발견된 음성, 화면 공유, 새로고침, LAN/TURN, 친구/DM,
  초대, 소리 차단 문제를 구현 가능한 작업 단위로 해결

## 현재 결론

- Stage M1부터 M10까지 코드 및 문서 수정은 완료되었다.
- 자동 검증으로 확인 가능한 범위는 통과했다.
- 실제 장비와 네트워크가 필요한 항목은 아직 수동 QA 게이트로 남아 있다.
- 특히 실제 마이크 장음 품질, 실제 다중 사용자 화면 공유 레이아웃,
  다른 PC에서의 HTTPS LAN 미디어 테스트, TURN/NAT 외부망 통화는 자동
  테스트만으로 완료 처리하면 안 된다.

## 수정 완료 항목

### M1. 실제 음성 끊김 진단 및 완화

수정 내용:

- 마이크 입력이 VAD에 의해 차단되지 않는지 확인했다.
- VAD는 말하는 중 표시와 입력 레벨 표시용으로만 유지했다.
- 브라우저 음성 처리 프리셋을 추가했다.
- 기본 프리셋을 `speech-stability`로 설정했다.
- 설정 화면에서 음성 처리 프리셋을 선택할 수 있도록 했다.
- 선택값은 로컬 환경 설정에 저장하되, 장치 라벨이나 원본 오디오 정보는
  저장하지 않도록 했다.

검증:

- `npm run lint:frontend` 통과
- `npm --prefix frontend run test -- --run src/composables/voiceMedia.test.ts` 통과
- `npm --prefix frontend run build` 통과

남은 확인:

- 실제 마이크로 긴 모음 또는 한 음절을 길게 말했을 때 끊김이 줄었는지는
  사람이 직접 들어야 한다.

### M2. 화면 공유 수신자 화면 중복 정리

수정 내용:

- 화면 공유 중인 원격 사용자가 별도 화면 공유 카드와 일반 참가자 카드로
  중복 표시되지 않도록 수정했다.
- 수신자는 공유자 1명당 하나의 화면 공유/참가자 조합만 보도록 정리했다.
- 자동 smoke 테스트에서 원격 공유자의 화면 타일은 1개, 중복 참가자 카드는
  0개인지 확인하도록 했다.

검증:

- `npm run lint:frontend` 통과
- `npm --prefix frontend run build` 통과
- `npm run smoke:realtime:browser` 통과
- 확인된 값:
  - `remoteSharingUserScreenTiles: 1`
  - `duplicateRemoteSharingParticipantCards: 0`

남은 확인:

- 실제 여러 사용자가 동시에 화면 공유할 때 4명이면 4개 구성만 나오는지
  수동 확인이 필요하다.

### M3. 새로고침 후 음성 재참여 복구

수정 내용:

- 마지막으로 접속한 음성 서버/채널 정보를 안전한 로컬 메타데이터로 저장한다.
- 새로고침 후 자동으로 마이크를 잡지 않고, 앱 자체 재참여 안내를 보여준다.
- 사용자가 재참여를 누르면 정상 마이크 권한 흐름을 통해 다시 접속한다.
- 안내를 닫거나 정상적으로 음성 채널을 나가면 복구 메타데이터를 지운다.

검증:

- `npm run lint:frontend` 통과
- `npm --prefix frontend run build` 통과
- `npm run smoke:realtime:browser` 통과
- 확인된 값:
  - `voiceRejoinPromptVisible: true`
  - `voiceRejoinRecovered: true`

남은 확인:

- 실제 브라우저 권한 프롬프트가 뜨는 환경에서 재참여 흐름이 자연스럽게
  동작하는지는 수동 확인이 필요하다.

### M4. 같은 LAN에서 HTTPS 미디어 테스트 경로 추가

수정 내용:

- `http://<LAN-IP>`에서는 브라우저가 마이크와 화면 캡처를 막을 수 있음을
  문서화했다.
- 로컬 인증서 기반 HTTPS LAN 프론트 실행 경로를 추가했다.
- `VITE_HTTPS_KEY_FILE`, `VITE_HTTPS_CERT_FILE`을 통해 Vite HTTPS 실행이
  가능하도록 했다.
- LAN 테스트 체크리스트를 문서화했다.

검증:

- `npm run lint:frontend` 통과
- `npm --prefix frontend run build` 통과

남은 확인:

- 실제 두 번째 PC에서 인증서를 신뢰시킨 뒤 `https://<host-ip>:5173`로 접속해
  마이크/화면 공유가 되는지 확인해야 한다.

### M5. TURN/NAT 준비도 점검

수정 내용:

- 안전한 TURN 준비도 확인 API를 추가했다.
- `GET /api/meta/voice/readiness`는 다음 값만 반환한다.
  - ICE 서버 수
  - STUN 설정 여부
  - TURN 설정 여부
- TURN URL, 계정, credential, ICE candidate, 토큰, 장치 라벨은 출력하지 않는다.
- `npm run check:voice:readiness` 명령을 추가했다.

검증:

- `npm run test:backend -- -q tests/test_api_routes.py::test_voice_readiness_omits_ice_server_credentials` 통과
- `npm run lint:backend` 통과
- `npm run test:backend` 통과
- `npm run check:voice:readiness` 통과
- 현재 로컬 Docker 환경은 `turn_configured: false`로 확인됨

남은 확인:

- 실제 TURN credential을 설정한 뒤 다른 네트워크에 있는 두 사용자가 음성과
  화면 공유를 성공해야 TURN/NAT 완료로 볼 수 있다.

### M6. 친구 요청과 온라인 상태 표시 정리

수정 내용:

- Friends 화면의 대기 탭을 친구 요청 의미로 명확히 정리했다.
- 수신한 요청과 보낸 요청을 별도 그룹으로 분리했다.
- Online/All 목록은 실제 친구 관계 기준으로 표시하도록 정리했다.
- 관계 업데이트 이벤트가 DM 목록과 참가자 상태에도 반영되도록 보강했다.

검증:

- `npm run lint:frontend` 통과
- `npm --prefix frontend run test -- --run src/stores/gatewayIdempotency.test.ts` 통과
- `npm --prefix frontend run build` 통과
- `npm run smoke:realtime:browser` 통과

남은 확인:

- 독립적인 presence update endpoint/event는 아직 별도 구현 범위가 아니다.
  실제 온라인/오프라인/자리비움 상태를 완전한 실시간 presence로 만들려면
  별도 Stage가 필요하다.

### M7. DM 표시 대상 정규화

수정 내용:

- 1:1 DM 목록에서 자기 자신이 아니라 상대방이 표시되도록 정규화했다.
- REST와 gateway payload 모두 현재 사용자 기준으로 DM 표시 이름과 수신자
  정보를 재계산한다.
- 메시지 작성자는 실제 작성자로 유지한다.

검증:

- `npm run lint:frontend` 통과
- `npm --prefix frontend run test -- --run src/stores/gatewayIdempotency.test.ts` 통과
- `npm --prefix frontend run build` 통과
- `npm run smoke:realtime:browser` 통과

남은 확인:

- 사용자가 실제 두 계정으로 DM을 주고받으며 목록 이름과 메시지 작성자가
  헷갈리지 않는지 확인하면 좋다.

### M8. 초대 모달 상태 분리 및 DM 초대 전송

수정 내용:

- 초대 코드 복사 상태와 친구별 초대 전송 상태를 분리했다.
- 특정 친구에게 초대를 보내면 해당 친구 row만 전송 상태가 바뀐다.
- 친구 초대 버튼은 DM을 열거나 만들고, 초대 코드를 DM 메시지로 전송한다.
- 하단 복사 버튼은 코드 복사 상태만 담당한다.

검증:

- `npm run lint:frontend` 통과
- `npm --prefix frontend run test -- --run src/composables/useInviteController.test.ts` 통과
- `npm --prefix frontend run build` 통과
- `npm run smoke:realtime:browser` 통과
- 확인된 값:
  - `inviteDmRealtime: true`

남은 확인:

- DM에서 초대 코드를 보고 바로 참여하는 UX는 현재 코드 입력 기반이다.
  클릭 가능한 직접 참여 링크 UX는 별도 개선 후보이다.

### M9. 소리 차단 동작 보강

수정 내용:

- 최초 구현은 원격 오디오만 mute하는 수준이어서 불완전했다.
- 재점검 후 Discord에 가깝게 수정했다.
- Deafen을 켜면:
  - 원격 참가자 소리가 로컬에서 들리지 않는다.
  - 내 마이크 track도 비활성화되어 송출되지 않는다.
  - 수동 mute 버튼은 비활성화된다.
  - 화면 공유는 계속 가능하다.
- Deafen을 끄면:
  - 원격 오디오가 다시 들린다.
  - deafen 전 수동 mute 상태를 복구한다.

검증:

- `npm run lint:frontend` 통과
- `npm --prefix frontend run build` 통과
- `npm run smoke:realtime:browser` 통과
- 확인된 값:
  - `remoteAudioMutedWhileDeafened: true`
  - `remoteAudioUnmutedAfterUndeafen: true`
  - `localMicrophoneMutedWhileDeafened: true`
  - `localMicrophoneRestoredAfterUndeafen: true`
  - `muteButtonDisabledWhileDeafened: true`

남은 확인:

- 실제 사용자가 deafen을 켰을 때 상대방에게 내 소리가 전달되지 않는지
  실제 브라우저 2계정으로 들어보는 확인이 필요하다.

### M10. 초대 권한 브라우저 QA

수정 내용:

- 서버 owner는 초대 버튼을 볼 수 있고 초대를 생성할 수 있다.
- 일반 member는 초대 버튼과 우클릭 초대 항목을 볼 수 없도록 했다.
- 일반 member가 API로 초대 생성을 시도하면 backend는 계속 `403`을 반환한다.
- raw `create invite permission required` 문구가 일반 UI에 노출되지 않도록 했다.
- 전역 context menu의 초대 항목도 `guilds.canCreateInvite` 기준으로 필터링했다.

검증:

- `npm run lint:frontend` 통과
- `npm --prefix frontend run build` 통과
- `docker compose up -d --build frontend`로 브라우저 테스트용 프론트 갱신
- `npm run smoke:realtime:browser` 통과
- 확인된 값:
  - `ownerInviteControlVisible: true`
  - `memberInviteControlHidden: true`
  - `memberContextInviteHidden: true`
  - `memberInviteApiForbidden: true`
  - `memberRawInvitePermissionHidden: true`

남은 확인:

- 실제 owner/member 계정으로 서버 메뉴, 상단 초대 버튼, 우클릭 메뉴를 직접
  눌러 UI가 기대대로 보이는지 확인하면 좋다.

## 자동 검증으로 확인한 범위

대표 검증 명령:

```powershell
npm run lint:frontend
npm --prefix frontend run build
npm run smoke:realtime:browser
```

추가로 단계별로 다음 명령도 실행되었다.

```powershell
npm --prefix frontend run test -- --run src/composables/voiceMedia.test.ts
npm --prefix frontend run test -- --run src/stores/gatewayIdempotency.test.ts
npm --prefix frontend run test -- --run src/composables/useInviteController.test.ts
npm run lint:backend
npm run test:backend
npm run check:voice:readiness
```

## 아직 수동으로 확인해야 하는 항목

자동 smoke는 같은 PC, fake device, 제한된 브라우저 자동화 환경을 기준으로 한다.
아래 항목은 실제 장비와 네트워크 조건이 필요하므로 자동 통과만으로 완료 처리하면
안 된다.

1. 실제 마이크 장음 품질
   - 한 음절을 길게 말했을 때 끊김이 없어졌는지 확인해야 한다.
   - 예: `아~~~~`를 10초 이상 말했을 때 중간에 잘리는지 확인.

2. 실제 화면 공유 레이아웃
   - 실제 screen picker로 공유했을 때 수신자 화면에서 공유자 1명당 하나의
     구성만 보이는지 확인해야 한다.
   - 여러 명이 공유할 때 카드 수가 과도하게 늘어나지 않는지 확인해야 한다.

3. 새로고침 후 실제 권한 재요청 흐름
   - 브라우저가 실제 마이크 권한을 다시 요청하는 상황에서 재참여 UX가 자연스러운지
     확인해야 한다.

4. 같은 LAN의 다른 PC 테스트
   - HTTP LAN이 아니라 신뢰된 HTTPS LAN 경로에서 테스트해야 한다.
   - 두 번째 PC에 인증서를 신뢰시킨 뒤 `https://<host-ip>:5173`로 접속해야 한다.

5. TURN/NAT 외부망 테스트
   - 현재 로컬은 `turn_configured: false`이다.
   - 실제 TURN credential 설정 후 서로 다른 네트워크에서 음성/화면 공유가 되는지
     확인해야 한다.

6. Presence 완성도
   - 현재 친구 관계 업데이트는 반영되지만, 완전한 온라인/오프라인/자리비움
     presence 시스템은 별도 기능으로 남아 있다.

7. DM 초대 직접 참여 UX
   - 현재는 DM으로 초대 코드를 보내는 수준이다.
   - Discord처럼 클릭 가능한 참여 링크 UX는 추후 개선 대상이다.

## 관련 커밋

- `ade4998 소리 차단 마이크 동작 보강`
- `8d8dfdb 초대 권한 브라우저 검증 추가`
- `a1148e5 소리 차단 원격 오디오 적용`
- `4736fd3 초대 DM 전송 상태 분리`
- `9be8ba8 DM 표시 대상 정규화`
- `911d891 친구 요청과 상태 표시 정리`
- `e82bf68 TURN 준비도 안전 점검 추가`
- `3e05b4f LAN HTTPS 개발 경로 추가`
- `0968fa3 음성 새로고침 재참여 복구 추가`
- `f9e7939 화면 공유 참여자 중복 정리`
- `d9aea4c 음성 처리 프리셋 추가`

## 다음 작업 추천

다음 작업은 자동화보다 실제 사용성 검증이 중요하다. 우선순위는 다음과 같다.

1. 실제 마이크 장음 품질 재테스트
2. 실제 화면 공유 다중 사용자 레이아웃 확인
3. 같은 LAN의 다른 PC에서 HTTPS 경로로 음성 참여 확인
4. TURN 설정 후 외부망 통화 확인
5. presence와 DM 초대 링크 UX를 별도 Stage로 분리해 구현
