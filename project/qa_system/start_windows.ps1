param([switch]$NoBrowser,[switch]$Review)
$ErrorActionPreference = 'Stop'
$appDir = $PSScriptRoot
$pythonExe = Join-Path $appDir '.venv-win/Scripts/python.exe'
$runtimeDir = Join-Path $appDir 'runtime'
$port = if ($Review) {8502} else {8501}
$entrypoint = if ($Review) {'review_app.py'} else {'app.py'}
$prefix = if ($Review) {'review-windows'} else {'streamlit-windows'}
$address = "http://127.0.0.1:$port"
if (-not (Test-Path -LiteralPath $pythonExe)) {
    throw 'Windows environment missing. Create .venv-win and install this project first; see README.'
}
New-Item -ItemType Directory -Force -Path $runtimeDir | Out-Null
function Test-AppHealth {
    try { return (Invoke-WebRequest "$address/_stcore/health" -UseBasicParsing -TimeoutSec 2).StatusCode -eq 200 }
    catch { return $false }
}
if (-not (Test-AppHealth)) {
    $process = Start-Process -FilePath $pythonExe -ArgumentList @('-I','-X','utf8','-m','streamlit','run',$entrypoint,'--server.address=127.0.0.1',"--server.port=$port",'--server.headless=true','--browser.gatherUsageStats=false') -WorkingDirectory $appDir -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runtimeDir "$prefix.stdout.log") -RedirectStandardError (Join-Path $runtimeDir "$prefix.stderr.log")
    $process.Id | Set-Content -LiteralPath (Join-Path $runtimeDir "$prefix.pid")
    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        if (Test-AppHealth) { $ready = $true; break }
        if ($process.HasExited) { break }
        Start-Sleep -Milliseconds 500
    }
    if (-not $ready) { throw "Startup failed. Check runtime/$prefix.stderr.log." }
}
Write-Output "OCS QA is running: $address"
if (-not $NoBrowser) { Start-Process $address }
