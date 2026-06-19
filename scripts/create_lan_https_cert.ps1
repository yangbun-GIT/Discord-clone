param(
  [string]$HostName = "",
  [string]$OutDir = "certs",
  [string]$PfxPassphrase = "discord-clone-local"
)

$ErrorActionPreference = "Stop"

function Get-DefaultLanAddress {
  $candidate = Get-NetIPConfiguration |
    Where-Object { $_.IPv4DefaultGateway -and $_.IPv4Address } |
    ForEach-Object { $_.IPv4Address } |
    Where-Object { $_.IPAddress -and $_.IPAddress -notlike "169.254*" -and $_.IPAddress -ne "127.0.0.1" } |
    Select-Object -First 1

  if (-not $candidate) {
    throw "Could not determine a LAN IPv4 address. Pass -HostName explicitly, for example -HostName 192.168.0.25."
  }

  return $candidate.IPAddress
}

function Remove-GeneratedCertFromMyStore {
  param([string]$Thumbprint)

  if ([string]::IsNullOrWhiteSpace($Thumbprint)) {
    return
  }

  $path = "Cert:\CurrentUser\My\$Thumbprint"
  if (Test-Path -LiteralPath $path) {
    Remove-Item -LiteralPath $path -Force
  }
}

if ([string]::IsNullOrWhiteSpace($HostName)) {
  $HostName = Get-DefaultLanAddress
}

$resolvedOutDir = Resolve-Path -LiteralPath "." | Select-Object -ExpandProperty Path
$resolvedOutDir = Join-Path $resolvedOutDir $OutDir
New-Item -ItemType Directory -Force -Path $resolvedOutDir | Out-Null

$pfxPath = Join-Path $resolvedOutDir "lan-dev.pfx"
$rootCerPath = Join-Path $resolvedOutDir "lan-dev-root-ca.cer"
$password = ConvertTo-SecureString -String $PfxPassphrase -Force -AsPlainText
$now = Get-Date
$expires = $now.AddYears(2)

$ip = [System.Net.IPAddress]::None
$isIpHost = [System.Net.IPAddress]::TryParse($HostName, [ref]$ip)
$sanParts = @("DNS=localhost", "IPAddress=127.0.0.1")
if ($isIpHost) {
  $sanParts = @("IPAddress=$HostName") + $sanParts
} else {
  $sanParts = @("DNS=$HostName") + $sanParts
}
$sanTextExtension = "2.5.29.17={text}$($sanParts -join '&')"

$rootCert = New-SelfSignedCertificate `
  -Type Custom `
  -Subject "CN=Discord Clone Local Development Root CA" `
  -KeyAlgorithm RSA `
  -KeyLength 2048 `
  -HashAlgorithm SHA256 `
  -KeyExportPolicy Exportable `
  -CertStoreLocation "Cert:\CurrentUser\My" `
  -KeyUsage CertSign, CRLSign, DigitalSignature `
  -TextExtension @("2.5.29.19={critical}{text}ca=TRUE") `
  -NotAfter $expires

$serverCert = New-SelfSignedCertificate `
  -Type Custom `
  -Subject "CN=$HostName" `
  -Signer $rootCert `
  -KeyAlgorithm RSA `
  -KeyLength 2048 `
  -HashAlgorithm SHA256 `
  -KeyExportPolicy Exportable `
  -CertStoreLocation "Cert:\CurrentUser\My" `
  -KeyUsage DigitalSignature, KeyEncipherment `
  -TextExtension @($sanTextExtension, "2.5.29.37={text}1.3.6.1.5.5.7.3.1") `
  -NotAfter $expires

try {
  Export-PfxCertificate -Cert $serverCert -FilePath $pfxPath -Password $password -Force | Out-Null
  Export-Certificate -Cert $rootCert -FilePath $rootCerPath -Force | Out-Null
} finally {
  Remove-GeneratedCertFromMyStore -Thumbprint $serverCert.Thumbprint
  Remove-GeneratedCertFromMyStore -Thumbprint $rootCert.Thumbprint
}

Write-Host "Created HTTPS LAN certificate for $HostName"
Write-Host "PFX:  $pfxPath"
Write-Host "Trust this Root CA on other devices: $rootCerPath"
Write-Host "Root CA thumbprint: $($rootCert.Thumbprint)"
Write-Host "Server certificate thumbprint: $($serverCert.Thumbprint)"

Write-Host ""
Write-Host "Run Docker HTTPS LAN with:"
Write-Host "  docker compose -f compose.yaml -f compose.https.yaml up -d --build"
Write-Host ""
Write-Host "Open from another device after trusting lan-dev-root-ca.cer:"
Write-Host "  https://$HostName`:5173"
