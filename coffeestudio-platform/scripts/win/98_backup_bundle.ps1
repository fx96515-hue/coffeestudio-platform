<#
CoffeeStudio Backup Bundle (prod-safe)

Creates a zip under .\backups\ with:
- key source folders (no .env)
- docker/compose diagnostics + logs
- schema-only pg_dump (best-effort)

Run from repo root:
  .\scripts\win\98_backup_bundle.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Get-Location).Path
$Ts = Get-Date -Format "yyyyMMdd_HHmmss"
$OutDir = Join-Path $RepoRoot "backups\bundle_$Ts"
$ZipPath = Join-Path $RepoRoot "backups\coffeestudio_backup_$Ts.zip"

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

function SafeRun {
  param([string]$Name, [scriptblock]$Block)
  try {
    $out = & $Block 2>&1 | Out-String
    $out | Set-Content -Encoding UTF8 (Join-Path $OutDir $Name)
  } catch {
    ("ERROR: " + $_.Exception.Message + "`n" + ($_.ScriptStackTrace | Out-String)) |
      Set-Content -Encoding UTF8 (Join-Path $OutDir $Name)
  }
}

function CopyIfExists {
  param([string]$RelPath)
  $src = Join-Path $RepoRoot $RelPath
  if (Test-Path $src) {
    $dst = Join-Path $OutDir $RelPath
    $dstDir = Split-Path -Parent $dst
    New-Item -ItemType Directory -Force -Path $dstDir | Out-Null
    Copy-Item -Force -Recurse -Path $src -Destination $dst
  }
}

# --- include sources (no secrets) ---
CopyIfExists "docker-compose.yml"
CopyIfExists "docker-compose.stack.yml"
CopyIfExists "docker-compose.override.yml"
CopyIfExists "compose"
CopyIfExists "scripts"

CopyIfExists "backend\app"
CopyIfExists "backend\alembic"
CopyIfExists "backend\migrations"
CopyIfExists "backend\requirements.txt"
CopyIfExists "backend\pyproject.toml"
CopyIfExists "backend\alembic.ini"

CopyIfExists ".env.example"
CopyIfExists "backend\.env.example"

# explicitly skip .env

# --- diagnostics ---
SafeRun "00_pwd.txt" { $RepoRoot }
SafeRun "01_powershell_version.txt" { $PSVersionTable | Format-List | Out-String }
SafeRun "02_git_status.txt" { git status --porcelain=v1 }
SafeRun "03_git_head.txt" { git rev-parse HEAD }

SafeRun "10_docker_version.txt" { docker version }
SafeRun "11_docker_info.txt" { docker info }
SafeRun "12_compose_version.txt" { docker compose version }
SafeRun "13_compose_config.txt" { docker compose config }
SafeRun "14_compose_ps.txt" { docker compose ps }

SafeRun "20_logs_backend.txt" { docker compose logs --no-color --tail 800 backend }
SafeRun "21_logs_worker.txt"  { docker compose logs --no-color --tail 800 worker }
SafeRun "22_logs_beat.txt"    { docker compose logs --no-color --tail 800 beat }
SafeRun "23_logs_frontend.txt"{ docker compose logs --no-color --tail 800 frontend }
SafeRun "25_logs_postgres.txt"{ docker compose logs --no-color --tail 800 postgres }
SafeRun "26_logs_redis.txt"   { docker compose logs --no-color --tail 800 redis }

SafeRun "30_db_schema_pg_dump.txt" {
  docker compose exec -T postgres sh -lc 'pg_dump --schema-only -U "${POSTGRES_USER:-coffeestudio}" "${POSTGRES_DB:-coffeestudio}"'
}

SafeRun "40_api_health.txt" { curl.exe -sS http://api.localhost/health }
SafeRun "41_ui_login_status.txt" { curl.exe -sS -o NUL -w "HTTP %{http_code}`n" http://ui.localhost/login }

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $ZipPath) | Out-Null
if (Test-Path $ZipPath) { Remove-Item -Force $ZipPath }

Compress-Archive -Path (Join-Path $OutDir "*") -DestinationPath $ZipPath -Force

Write-Host "BACKUP DONE ✅"
Write-Host "ZIP: $ZipPath"
Write-Host "Folder: $OutDir"
