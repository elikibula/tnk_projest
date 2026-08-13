param([Parameter(Mandatory=$true)][string]$BackupFile,[Parameter(Mandatory=$true)][string]$TargetDatabaseUrl)
$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $BackupFile)) { throw "Backup file not found." }
$databaseName = ([Uri]$TargetDatabaseUrl).AbsolutePath.Trim("/").ToLowerInvariant()
if (-not ($databaseName.Contains("stage") -or $databaseName.Contains("rehearsal") -or $databaseName.Contains("test"))) {
    throw "Restore target database name must clearly identify staging, rehearsal, or test use."
}
& pg_restore --exit-on-error --no-owner --dbname=$TargetDatabaseUrl $BackupFile
if ($LASTEXITCODE -ne 0) { throw "pg_restore failed with exit code $LASTEXITCODE." }
Write-Output "DATABASE_RESTORE_TARGET=$databaseName"
