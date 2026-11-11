param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$appDir = $PSScriptRoot
$pythonExe = Join-Path $appDir '.venv-win/Scripts/python.exe'
$runtimeDir = Join-Path $appDir 'runtime'
$address = 'http://127.0.0.1:8501'
if (-not (Test-Path -LiteralPath $pythonExe)) {
    throw 'Windows environment missing. Create .venv-win and install this project first; see README.'
}
New-Item -ItemType Directory -Force -Path $runtimeDir | Out-Null
function Test-AppHealth {
    try { return (Invoke-WebRequest "$address/_stcore/health" -UseBasicParsing -TimeoutSec 2).StatusCode -eq 200 }
    catch { return $false }
}
if (-not (Test-AppHealth)) {
    $process = Start-Process -FilePath $pythonExe -ArgumentList @('-I','-X','utf8','-m','streamlit','run','app.py','--server.address=127.0.0.1','--server.port=8501','--server.headless=true','--browser.gatherUsageStats=false') -WorkingDirectory $appDir -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runtimeDir 'streamlit-windows.stdout.log') -RedirectStandardError (Join-Path $runtimeDir 'streamlit-windows.stderr.log')
    $process.Id | Set-Content -LiteralPath (Join-Path $runtimeDir 'streamlit-windows.pid')
    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        if (Test-AppHealth) { $ready = $true; break }
        if ($process.HasExited) { break }
        Start-Sleep -Milliseconds 500
    }
    if (-not $ready) { throw 'Startup failed. Check runtime/streamlit-windows.stderr.log.' }
}
Write-Output "OCS QA is running: $address"
if (-not $NoBrowser) { Start-Process $address }
