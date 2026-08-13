param([Parameter(Mandatory=$true)][string]$OutputFile)
$ErrorActionPreference = "Stop"
if (-not $env:DATABASE_URL) { throw "DATABASE_URL is required." }
$parent = Split-Path -Parent ([System.IO.Path]::GetFullPath($OutputFile))
if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent | Out-Null }
& pg_dump --format=custom --no-owner --file=$OutputFile $env:DATABASE_URL
if ($LASTEXITCODE -ne 0) { throw "pg_dump failed with exit code $LASTEXITCODE." }
$hash = (Get-FileHash -LiteralPath $OutputFile -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Output "DATABASE_BACKUP=$([System.IO.Path]::GetFullPath($OutputFile))"
Write-Output "DATABASE_SHA256=$hash"
