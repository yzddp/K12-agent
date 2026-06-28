<#
.SYNOPSIS
  修远 AI 学习辅导员 — 升级脚本
.DESCRIPTION
  更新数据库 schema、同步模板配置、重启 gateway
  注意：此脚本不覆盖 USER.md（已在 .gitignore 中），模板变更请手动合并
#>

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  修远 — 升级" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 步骤 1: 检查 USER.template.md 变更
Write-Host "[1/4] 检查 USER.template.md 变更..." -ForegroundColor Yellow
$userFile = "$ScriptDir\USER.md"
$userTemplate = "$ScriptDir\USER.template.md"
if ((Test-Path $userFile) -and (Test-Path $userTemplate)) {
    $userLines = (Get-Content $userFile).Count
    $tmplLines = (Get-Content $userTemplate).Count
    if ($userLines -ne $tmplLines) {
        Write-Host "  [INFO] USER.template.md 已更新（$tmplLines 行 vs 你的 $userLines 行）" -ForegroundColor Yellow
        Write-Host "  请手动合并变更：diff USER.md USER.template.md" -ForegroundColor Yellow
    } else {
        Write-Host "  [OK] 模板无变更" -ForegroundColor Green
    }
} else {
    Write-Host "  [SKIP] USER.md 或 USER.template.md 不存在" -ForegroundColor Yellow
}

# 步骤 2: 更新数据库 schema
Write-Host "[2/4] 更新数据库 schema..." -ForegroundColor Yellow
try {
    py "$ScriptDir\scripts\init_db.py"
    Write-Host "  [OK] 数据库已更新" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] 数据库更新失败: $_" -ForegroundColor Red
    exit 1
}

# 步骤 3: 检查 CHANGELOG
Write-Host "[3/4] 检查版本变更..." -ForegroundColor Yellow
if (Test-Path "$ScriptDir\CHANGELOG.md") {
    Write-Host "  请查看 CHANGELOG.md 了解此版本变更" -ForegroundColor White
}
Write-Host "  [OK] 检查完成" -ForegroundColor Green

# 步骤 4: 重启 gateway
Write-Host "[4/4] 重启 Gateway..." -ForegroundColor Yellow
try {
    openclaw gateway restart
    Start-Sleep -Seconds 3
    openclaw gateway status
    Write-Host "  [OK] Gateway 已重启" -ForegroundColor Green
} catch {
    Write-Host "  请手动重启: openclaw gateway restart" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "升级完成！" -ForegroundColor Green
