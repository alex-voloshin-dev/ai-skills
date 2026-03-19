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
    @{ Source = ".claude"; Target = Join-Path $HomeDir ".claude" },
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

    $sourceFiles = Get-ChildItem -LiteralPath $SourceDir -Recurse -File
    $sourceIndex = @{}

    foreach ($file in $sourceFiles) {
        $relativePath = $file.FullName.Substring($SourceDir.Length).TrimStart('\', '/')
        $sourceIndex[$relativePath] = $true

        $targetFile = Join-Path $TargetDir $relativePath
        $targetParent = Split-Path -Parent $targetFile
        New-Item -ItemType Directory -Force -Path $targetParent | Out-Null
        Copy-Item -LiteralPath $file.FullName -Destination $targetFile -Force
    }

    $targetFiles = Get-ChildItem -LiteralPath $TargetDir -Recurse -File -ErrorAction SilentlyContinue
    foreach ($file in $targetFiles) {
        $relativePath = $file.FullName.Substring($TargetDir.Length).TrimStart('\', '/')
        if (-not $sourceIndex.ContainsKey($relativePath)) {
            Remove-Item -LiteralPath $file.FullName -Force
        }
    }

    $targetDirs = Get-ChildItem -LiteralPath $TargetDir -Recurse -Directory -ErrorAction SilentlyContinue |
        Sort-Object { $_.FullName.Length } -Descending

    foreach ($dir in $targetDirs) {
        if ((Get-ChildItem -LiteralPath $dir.FullName -Force | Measure-Object).Count -eq 0) {
            Remove-Item -LiteralPath $dir.FullName -Force
        }
    }
}

Write-Host "Installing AI assets into $HomeDir" -ForegroundColor Cyan

foreach ($mapping in $Mappings) {
    $sourceDir = Join-Path $ScriptDir $mapping.Source
    Sync-Directory -SourceDir $sourceDir -TargetDir $mapping.Target
    Write-Host "[ok] $($mapping.Source) -> $($mapping.Target)" -ForegroundColor Green
}

Write-Host "Done." -ForegroundColor Cyan
