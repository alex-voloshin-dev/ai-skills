param(
    [string]$HomeDir = $env:USERPROFILE
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($HomeDir)) {
    throw "HomeDir is not set. Pass -HomeDir explicitly."
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$HomeDir = [System.IO.Path]::GetFullPath($HomeDir)

$Mappings = @(
    # v0.2.0: .claude/ legacy package was removed. Claude Code users should
    # install the plugin from .\plugin\ via:
    #   claude --plugin-dir "$ScriptDir\plugin"
    # or after publishing:
    #   /plugin marketplace add alex-voloshin/ai-assets
    #   /plugin install ai-assets@ai-assets
    # See plugin\README.md for full install + usage.
    @{ Source = ".agents"; Target = Join-Path $HomeDir ".agents" },
    @{ Source = ".codex"; Target = Join-Path $HomeDir ".codex" },
    @{ Source = ".windsurf"; Target = Join-Path $HomeDir ".windsurf" }
)

function Sync-Directory {
    param(
        [Parameter(Mandatory = $true)][string]$SourceDir,
        [Parameter(Mandatory = $true)][string]$TargetDir
    )

    if (-not (Test-Path -LiteralPath $SourceDir)) {
        throw "Source directory not found: $SourceDir"
    }

    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

    $sourceFiles = Get-ChildItem -LiteralPath $SourceDir -Recurse -File | Where-Object {
        $_.Name -ne "settings.local.json" -and
        $_.DirectoryName -notmatch '(^|\\)__pycache__(\\|$)' -and
        @('.pyc', '.pyo') -notcontains $_.Extension
    }
    $sourceIndex = @{}

    foreach ($file in $sourceFiles) {
        $relativePath = $file.FullName.Substring($SourceDir.Length).TrimStart('\', '/')
        $sourceIndex[$relativePath] = $true

        $targetFile = Join-Path $TargetDir $relativePath
        $targetParent = Split-Path -Parent $targetFile
        New-Item -ItemType Directory -Force -Path $targetParent | Out-Null
        Copy-Item -LiteralPath $file.FullName -Destination $targetFile -Force
    }

    $skipExtensions = @('.sqlite', '.sqlite-shm', '.sqlite-wal', '.log')
    $targetFiles = Get-ChildItem -LiteralPath $TargetDir -Recurse -File -ErrorAction SilentlyContinue
    foreach ($file in $targetFiles) {
        $relativePath = $file.FullName.Substring($TargetDir.Length).TrimStart('\', '/')
        if (-not $sourceIndex.ContainsKey($relativePath)) {
            if ($skipExtensions -contains $file.Extension) {
                continue
            }
            try {
                Remove-Item -LiteralPath $file.FullName -Force -ErrorAction Stop
            } catch {
                Write-Warning "Skipping locked or protected file: $($file.FullName)"
            }
        }
    }

    $targetDirs = Get-ChildItem -LiteralPath $TargetDir -Recurse -Directory -ErrorAction SilentlyContinue |
        Sort-Object { $_.FullName.Length } -Descending

    foreach ($dir in $targetDirs) {
        if ((Get-ChildItem -LiteralPath $dir.FullName -Force | Measure-Object).Count -eq 0) {
            try {
                Remove-Item -LiteralPath $dir.FullName -Force -ErrorAction Stop
            } catch {
                Write-Warning "Skipping directory cleanup: $($dir.FullName)"
            }
        }
    }
}

function Set-JsonFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][object]$Data
    )

    $json = $Data | ConvertTo-Json -Depth 100
    [System.IO.File]::WriteAllText($Path, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
}

Write-Host "Installing AI assets into $HomeDir" -ForegroundColor Cyan

foreach ($mapping in $Mappings) {
    $sourceDir = Join-Path $ScriptDir $mapping.Source
    Sync-Directory -SourceDir $sourceDir -TargetDir $mapping.Target
    Write-Host "[ok] $($mapping.Source) -> $($mapping.Target)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Note: Claude Code is no longer installed via this script (v0.2.0+)." -ForegroundColor Yellow
Write-Host "Use the plugin layout instead:" -ForegroundColor Yellow
Write-Host "  claude --plugin-dir `"$ScriptDir\plugin`"" -ForegroundColor Yellow
Write-Host ""

Write-Host "Done." -ForegroundColor Cyan
