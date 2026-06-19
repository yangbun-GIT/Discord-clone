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

function Convert-ToPem {
  param(
    [string]$Label,
    [byte[]]$Bytes
  )

  $base64 = [Convert]::ToBase64String($Bytes, [Base64FormattingOptions]::InsertLineBreaks)
  return "-----BEGIN $Label-----`n$base64`n-----END $Label-----`n"
}

if ([string]::IsNullOrWhiteSpace($HostName)) {
  $HostName = Get-DefaultLanAddress
}

$resolvedOutDir = Resolve-Path -LiteralPath "." | Select-Object -ExpandProperty Path
$resolvedOutDir = Join-Path $resolvedOutDir $OutDir
New-Item -ItemType Directory -Force -Path $resolvedOutDir | Out-Null

$pfxPath = Join-Path $resolvedOutDir "lan-dev.pfx"
$certPath = Join-Path $resolvedOutDir "lan-dev-cert.pem"
$cerPath = Join-Path $resolvedOutDir "lan-dev-cert.cer"

$rsa = [System.Security.Cryptography.RSA]::Create(2048)
$subject = "CN=$HostName"
$request = [System.Security.Cryptography.X509Certificates.CertificateRequest]::new(
  $subject,
  $rsa,
  [System.Security.Cryptography.HashAlgorithmName]::SHA256,
  [System.Security.Cryptography.RSASignaturePadding]::Pkcs1
)

$san = [System.Security.Cryptography.X509Certificates.SubjectAlternativeNameBuilder]::new()
$ip = [System.Net.IPAddress]::None
if ([System.Net.IPAddress]::TryParse($HostName, [ref]$ip)) {
  $san.AddIpAddress($ip)
} else {
  $san.AddDnsName($HostName)
}
$san.AddDnsName("localhost")
$san.AddIpAddress([System.Net.IPAddress]::Parse("127.0.0.1"))
$request.CertificateExtensions.Add($san.Build())
$request.CertificateExtensions.Add(
  [System.Security.Cryptography.X509Certificates.X509BasicConstraintsExtension]::new($false, $false, 0, $true)
)
$request.CertificateExtensions.Add(
  [System.Security.Cryptography.X509Certificates.X509KeyUsageExtension]::new(
    [System.Security.Cryptography.X509Certificates.X509KeyUsageFlags]::DigitalSignature -bor
      [System.Security.Cryptography.X509Certificates.X509KeyUsageFlags]::KeyEncipherment,
    $true
  )
)

$serverAuthOid = [System.Security.Cryptography.Oid]::new("1.3.6.1.5.5.7.3.1")
$eku = [System.Security.Cryptography.X509Certificates.X509EnhancedKeyUsageExtension]::new(
  [System.Security.Cryptography.OidCollection]::new(),
  $false
)
$eku.EnhancedKeyUsages.Add($serverAuthOid) | Out-Null
$request.CertificateExtensions.Add($eku)

$notBefore = [System.DateTimeOffset]::UtcNow.AddDays(-1)
$notAfter = $notBefore.AddYears(2)
$certificate = $request.CreateSelfSigned($notBefore, $notAfter)

Set-Content -LiteralPath $certPath -Value (Convert-ToPem "CERTIFICATE" $certificate.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)) -NoNewline
[System.IO.File]::WriteAllBytes($pfxPath, $certificate.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Pfx, $PfxPassphrase))
[System.IO.File]::WriteAllBytes($cerPath, $certificate.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert))

Write-Host "Created HTTPS LAN certificate for $HostName"
Write-Host "PFX:  $pfxPath"
Write-Host "Cert: $certPath"
Write-Host "Trust file for other devices: $cerPath"
Write-Host "Thumbprint: $($certificate.Thumbprint)"

Write-Host ""
Write-Host "Run Docker HTTPS LAN with:"
Write-Host "  docker compose -f compose.yaml -f compose.https.yaml up -d --build"
Write-Host ""
Write-Host "Open from another device after trusting lan-dev-cert.cer:"
Write-Host "  https://$HostName`:5173"
