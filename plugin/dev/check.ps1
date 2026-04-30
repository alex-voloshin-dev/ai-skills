# Thin wrapper: run the local validator from any cwd.
# Usage:  powershell -ExecutionPolicy Bypass -File plugin\dev\check.ps1 [--quiet] [--json] [--strict]
# Or:     pwsh plugin\dev\check.ps1 [...]

$ErrorActionPreference = 'Stop'
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $python) { $python = Get-Command python3 -ErrorAction SilentlyContinue }
if ($null -eq $python) {
    Write-Error 'Python not found on PATH. Install Python 3.10+ and re-run.'
    exit 1
}
& $python.Source (Join-Path $dir 'validate.py') @args
exit $LASTEXITCODE
