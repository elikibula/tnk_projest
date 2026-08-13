param(
    [string]$CompilerPath = ""
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$version = "3.4.17"
$expectedHash = "67f1c5e3f5a03406a7bf5badf5ada09b79f3ae78ec43450c15f7e983068da346"
$temporaryCompiler = $false

if (-not $CompilerPath) {
    $CompilerPath = Join-Path ([System.IO.Path]::GetTempPath()) "tnk-tailwindcss-$version.exe"
    $temporaryCompiler = $true
    if (-not (Test-Path -LiteralPath $CompilerPath)) {
        Invoke-WebRequest -UseBasicParsing "https://github.com/tailwindlabs/tailwindcss/releases/download/v$version/tailwindcss-windows-x64.exe" -OutFile $CompilerPath
    }
}

$actualHash = (Get-FileHash -LiteralPath $CompilerPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actualHash -ne $expectedHash) {
    throw "Tailwind compiler checksum mismatch. Expected $expectedHash but received $actualHash."
}

Push-Location $projectRoot
try {
    & $CompilerPath -c tailwind.config.js -i frontend/tailwind.css -o backend/static/css/tailwind.css --minify
    if ($LASTEXITCODE -ne 0) { throw "Tailwind build failed with exit code $LASTEXITCODE." }
}
finally {
    Pop-Location
    if ($temporaryCompiler -and (Test-Path -LiteralPath $CompilerPath)) {
        Remove-Item -LiteralPath $CompilerPath -Force
    }
}
