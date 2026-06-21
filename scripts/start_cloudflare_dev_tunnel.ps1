param(
  [string]$Origin = "https://localhost:5173"
)

$ErrorActionPreference = "Stop"

$cloudflared = Get-Command cloudflared -ErrorAction SilentlyContinue
if (-not $cloudflared) {
  Write-Error "cloudflared를 찾을 수 없습니다. Cloudflare 공식 cloudflared 설치 후 다시 실행하세요."
  exit 1
}

try {
  $response = Invoke-WebRequest -Uri $Origin -UseBasicParsing -TimeoutSec 5
} catch {
  try {
    curl.exe -k -s -f "$Origin/" | Out-Null
  } catch {
    Write-Error "로컬 origin에 연결할 수 없습니다: $Origin. 먼저 npm run docker:up:https:detached 를 실행하세요."
    exit 1
  }
}

Write-Host "Cloudflare Quick Tunnel을 Vite 개발 서버에 연결합니다."
Write-Host "Origin: $Origin"
Write-Host "수정 사항은 Vite 개발 서버를 통해 Cloudflare URL에도 바로 반영됩니다."
Write-Host "종료하려면 Ctrl+C를 누르세요."

& $cloudflared.Source tunnel --url $Origin --no-tls-verify
