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

function Update-ClaudeHomeSettings {
    param(
        [Parameter(Mandatory = $true)][string]$ClaudeHome
    )

    $settingsPath = Join-Path $ClaudeHome "settings.json"
    if (-not (Test-Path -LiteralPath $settingsPath)) {
        return
    }

    $settings = Get-Content -LiteralPath $settingsPath -Raw | ConvertFrom-Json -Depth 100
    $scriptDir = (Join-Path $ClaudeHome "hooks\scripts").Replace('\', '/')
    $commandMap = @{
        "log-actions.py" = "python3 `"$scriptDir/log-actions.py`""
        "block-secrets-in-code.py" = "python3 `"$scriptDir/block-secrets-in-code.py`""
        "block-dangerous-commands.py" = "python3 `"$scriptDir/block-dangerous-commands.py`""
        "block-sensitive-files.py" = "python3 `"$scriptDir/block-sensitive-files.py`""
    }

    foreach ($phase in @("PreToolUse", "PostToolUse")) {
        if (-not ($settings.hooks.PSObject.Properties.Name -contains $phase)) {
            continue
        }

        foreach ($rule in $settings.hooks.$phase) {
            if (-not ($rule.PSObject.Properties.Name -contains "hooks")) {
                continue
            }

            foreach ($hook in $rule.hooks) {
                $command = [string]$hook.command
                foreach ($key in $commandMap.Keys) {
                    if ($command -like "*$key*") {
                        $hook.command = $commandMap[$key]
                        break
                    }
                }
            }
        }
    }

    Set-JsonFile -Path $settingsPath -Data $settings

    foreach ($configName in @("logging-hooks.json", "security-hooks.json")) {
        $configPath = Join-Path $ClaudeHome "hooks\configs\$configName"
        if (-not (Test-Path -LiteralPath $configPath)) {
            continue
        }

        $config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json -Depth 100
        foreach ($hookGroup in $config.hooks.PSObject.Properties) {
            foreach ($hook in $hookGroup.Value) {
                $command = [string]$hook.command
                foreach ($key in $commandMap.Keys) {
                    if ($command -like "*$key*") {
                        $hook.command = $commandMap[$key]
                        break
                    }
                }
            }
        }

        Set-JsonFile -Path $configPath -Data $config
    }
}

Write-Host "Installing AI assets into $HomeDir" -ForegroundColor Cyan

foreach ($mapping in $Mappings) {
    $sourceDir = Join-Path $ScriptDir $mapping.Source
    Sync-Directory -SourceDir $sourceDir -TargetDir $mapping.Target
    Write-Host "[ok] $($mapping.Source) -> $($mapping.Target)" -ForegroundColor Green
}

Update-ClaudeHomeSettings -ClaudeHome (Join-Path $HomeDir ".claude")
Write-Host "[ok] patched ~/.claude hook commands for global runtime" -ForegroundColor Green

Write-Host "Done." -ForegroundColor Cyan
