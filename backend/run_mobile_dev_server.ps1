$ErrorActionPreference = 'Stop'

$backendDirectory = $PSScriptRoot
$python = Join-Path (Split-Path $backendDirectory -Parent) 'tnk_venv\Scripts\python.exe'

Set-Location $backendDirectory
$localAddresses = [Net.Dns]::GetHostAddresses([Net.Dns]::GetHostName()) |
    Where-Object { $_.AddressFamily -eq [Net.Sockets.AddressFamily]::InterNetwork } |
    ForEach-Object { $_.IPAddressToString }
$env:DJANGO_ALLOWED_HOSTS = (@('localhost', '127.0.0.1') + $localAddresses | Select-Object -Unique) -join ','
Write-Host 'Starting TNK Django development server on http://0.0.0.0:8000/'
Write-Host "Allowed development hosts: $env:DJANGO_ALLOWED_HOSTS"
& $python manage.py runserver 0.0.0.0:8000 --noreload
exit $LASTEXITCODE
