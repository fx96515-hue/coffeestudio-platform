Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. "$PSScriptRoot\lib\http_json.ps1"

$BASE = "http://api.localhost"

Write-Host "== Health"
JsonGet "$BASE/health" | ConvertTo-Json -Depth 10 | Out-Host

Write-Host "== Login"
# TODO: adjust creds if you changed bootstrap
$login = JsonPost "$BASE/auth/login" @{ email="admin@coffeestudio.com"; password="adminadmin" }
if (-not $login.access_token) {
  throw ("No access_token returned from /auth/login. Response: " + ($login | ConvertTo-Json -Depth 10))
}
$AUTH = @{ Authorization = ("Bearer " + $login.access_token) }

Write-Host "== /auth/me"
JsonGet "$BASE/auth/me" $AUTH | ConvertTo-Json -Depth 10 | Out-Host

Write-Host "== KB seed"
JsonPost "$BASE/kb/seed" @{} $AUTH | ConvertTo-Json -Depth 10 | Out-Host

Write-Host "== KB query (logistics,de)"
JsonGet "$BASE/kb/?category=logistics&language=de" $AUTH | ConvertTo-Json -Depth 50 | Out-Host

Write-Host "SMOKE OK"
