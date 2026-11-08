param(
 [string]$Node='',
 [string]$Python='python',
 [string]$OutputDir=(Split-Path -Parent $PSScriptRoot)
)
$ErrorActionPreference='Stop'
if(!$Node){
 $found=Get-Command node -ErrorAction SilentlyContinue
 if($found){$Node=$found.Source}
 else{$Node='C:/Users/44282/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'}
}
$build=Join-Path $OutputDir '.build'
New-Item -ItemType Directory -Force -Path $build | Out-Null
$raw=Join-Path $build 'candidate-raw.pptx'
$candidate=Join-Path $build 'candidate.pptx'
& $Python (Join-Path $PSScriptRoot 'prepare_content.py')
if($LASTEXITCODE){throw 'Content generation failed'}
& $Node (Join-Path $PSScriptRoot 'build_deck.cjs') $raw
if($LASTEXITCODE){throw 'PPTX generation failed'}
& $Python (Join-Path $PSScriptRoot 'normalize_package.py') $raw $candidate
if($LASTEXITCODE){throw 'Package normalization failed'}
& (Join-Path $PSScriptRoot 'render_and_validate.ps1') -Candidate $candidate -OutputDir $OutputDir
& $Python (Join-Path $PSScriptRoot 'validate_deliverables.py')
if($LASTEXITCODE){throw 'Validation failed; inspect validation/deliverable-checks.json'}
