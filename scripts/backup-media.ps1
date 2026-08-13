param(
    [Parameter(Mandatory=$true)][string]$MediaRoot,
    [Parameter(Mandatory=$true)][string]$OutputFile
)
$ErrorActionPreference = "Stop"
$source = (Resolve-Path -LiteralPath $MediaRoot).Path
$parent = Split-Path -Parent ([System.IO.Path]::GetFullPath($OutputFile))
if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent | Out-Null }
if (Test-Path -LiteralPath $OutputFile) { throw "Media backup already exists: $OutputFile" }
Compress-Archive -Path (Join-Path $source "*") -DestinationPath $OutputFile -CompressionLevel Optimal
$hash = (Get-FileHash -LiteralPath $OutputFile -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Output "MEDIA_BACKUP=$([System.IO.Path]::GetFullPath($OutputFile))"
Write-Output "MEDIA_SHA256=$hash"
