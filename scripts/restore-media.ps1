param(
    [Parameter(Mandatory=$true)][string]$BackupFile,
    [Parameter(Mandatory=$true)][string]$TargetDirectory
)
$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $BackupFile)) { throw "Media backup not found." }
$target = [System.IO.Path]::GetFullPath($TargetDirectory)
if (Test-Path -LiteralPath $target) {
    if (Get-ChildItem -LiteralPath $target -Force | Select-Object -First 1) {
        throw "Media restore target must be empty: $target"
    }
} else {
    New-Item -ItemType Directory -Path $target | Out-Null
}
Expand-Archive -LiteralPath $BackupFile -DestinationPath $target
Write-Output "MEDIA_RESTORE_TARGET=$target"
