# Friends/DM 사용성 보강 체크리스트

## 목적

이 문서는 사용자가 Friends/DM 화면의 현재 구현 상태를 빠르게 확인하기 위한
한국어 체크리스트다. Codex가 실제 구현에 참고하는 영문 문서는
`docs/remediation-tasks/friends-dm-usability-implementation-reference.md`이고,
상세 이슈 원본은 `docs/remediation-tasks/friends-home-remediation-2026-06-20.md`다.

이번 작업의 범위는 단순 꾸밈이 아니라 실제 사용성을 막는 문제를 줄이는 것이다.
버튼이 보이면 실제 기능을 하거나, 아직 구현 전이면 활성 버튼처럼 보이지 않게
해야 한다.

## 2026-06-20 구현 상태

### 구현 완료

1. 친구 프로필 보기
   - 친구 목록, 현재 활동 패널, 우클릭 메뉴에서 프로필 팝업을 열 수 있다.
   - 프로필에는 사용자명, 핸들, 상태, 활동, 관계 상태, 메시지/통화/알림 끄기
     액션이 표시된다.

2. 대화 알림 끄기
   - DM별 알림 끄기 상태를 로컬 선호 설정으로 저장한다.
   - 음소거한 DM도 메시지는 정상 수신되지만, 비활성 DM unread 강조는 증가하지
     않는다.

3. 새 DM 시작
   - 좌측 DM 사이드바의 `+` 버튼과 빠른 전환기의 새 DM 시작 버튼이 친구 선택
     창을 연다.
   - 친구를 선택하면 기존 DM을 열거나 새 DM을 생성한다.

4. 친구/DM 우클릭 메뉴
   - 친구 row와 DM row가 대상 ID를 전달한다.
   - 우클릭 메뉴는 클릭한 대상의 프로필 보기, 메시지 보내기, 알림 끄기,
     통화 진입 액션으로 연결된다.

5. 친구 요청 도착 피드백
   - 새 받은 친구 요청이 realtime `RELATIONSHIP_UPDATE`로 들어오면 앱 내부
     알림을 띄우고 친구 요청 탭을 열 수 있는 상태로 전환한다.

6. 메시지 하단 기준 표시
   - DM과 서버 텍스트 채팅은 DM/채널 전환 시 최신 메시지 쪽으로 이동한다.
   - 사용자가 과거 메시지를 보고 있으면 강제로 아래로 끌어내리지 않고,
     `최신 메시지로 이동` 버튼을 표시한다.

7. DM 화면 액션
   - 선택된 DM 화면 안에서 프로필 보기, 통화 진입, 알림 끄기 액션을 사용할 수
     있다.

### 부분 구현 또는 후속 작업

1. 친구/DM 통화 시작
   - 현재 버튼은 대상 DM을 열고 안내를 보여주는 수준이다.
   - 실제 1:1 DM 통화는 아직 완료가 아니다.
   - 현재 백엔드 음성 게이트웨이는 서버 음성 채널 구독을 기준으로 음성 상태와
     WebRTC signaling을 검증한다.
   - 진짜 DM 통화를 완료하려면 DM 전용 private call room 또는 DM voice mapping
     백엔드 확장이 필요하다.

2. 친구 요청 배지
   - 요청 도착 알림과 pending 탭 포커스는 구현됐다.
   - `@me` 또는 DM 사이드바에 계속 남는 친구 요청 배지는 아직 후속 작업이다.

3. DM 검색과 그룹 DM 정보
   - DM 화면의 기본 액션은 연결됐다.
   - Discord처럼 강한 DM 내부 검색, 그룹 멤버 상세 패널, 통화 기록 UI는 아직
     후속 작업이다.

## 수동 확인 방법

1. 두 계정으로 로그인한다.
2. A가 B에게 친구 요청을 보낸다.
3. B 화면에서 앱 내부 알림과 친구 요청 탭 반응을 확인한다.
4. 친구 목록에서 프로필 보기, 메시지 보내기, 알림 끄기, 우클릭 메뉴를 확인한다.
5. 좌측 DM `+` 버튼으로 친구를 선택해 새 DM을 열 수 있는지 확인한다.
6. 긴 DM 또는 서버 채팅에서 새 메시지가 아래에 붙고, 과거 메시지를 보고 있을 때
   최신 메시지 이동 버튼이 나타나는지 확인한다.
7. DM 알림 끄기 후 다른 계정이 메시지를 보내도 해당 DM unread 강조가 증가하지
   않는지 확인한다.
8. 친구/DM 통화 버튼은 실제 private call 완료가 아니라 DM 진입 및 안내 수준임을
   확인한다.

## 다음 보강 후보

- 실제 DM private voice call room 설계와 백엔드 게이트웨이 확장
- 친구 요청 배지를 `@me`/사이드바에 안정적으로 표시
- DM 내부 메시지 검색
- 그룹 DM 멤버 패널과 그룹 관리 UX
- 모바일/좁은 화면에서 새 DM dialog와 프로필 dialog 재검증

## 이번 패스 검증 결과

- `npm run lint:frontend` 통과
- `npm run test:frontend` 통과: 7개 파일, 46개 테스트
- `npm --prefix frontend run build` 통과
- `npm run smoke:realtime:browser:https` 통과
  - 서버 텍스트 realtime
  - DM realtime
  - 초대 DM realtime
  - 음성 smoke
  - 화면 공유 smoke
  - 새로고침 후 음성 복구
  - `browserErrors: 0`
- `npm run docker:up:https:detached`로 재빌드/재기동 후
  `npm run check:submission:local` 통과
- 재빌드 후 `npm run smoke:realtime:browser:https` 재통과
- `git diff --check` 통과: 줄바꿈 경고만 있음
