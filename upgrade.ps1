<#
.SYNOPSIS
  修远 AI 学习辅导员 — 升级脚本
.DESCRIPTION
  更新数据库 schema、重启 gateway
#>

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  修远 — 升级" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 步骤 1: 更新数据库 schema
Write-Host "[1/3] 更新数据库 schema..." -ForegroundColor Yellow
try {
    py "$ScriptDir\scripts\init_db.py"
    Write-Host "  [OK] 数据库已更新" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] 数据库更新失败: $_" -ForegroundColor Red
    exit 1
}

# 步骤 2: 检查是否有新配置项
Write-Host "[2/3] 检查配置更新..." -ForegroundColor Yellow
if (Test-Path "$ScriptDir\CHANGELOG.md") {
    Write-Host "  请查看 CHANGELOG.md 了解此版本变更" -ForegroundColor White
}
Write-Host "  [OK] 检查完成" -ForegroundColor Green

# 步骤 3: 重启 gateway
Write-Host "[3/3] 重启 Gateway..." -ForegroundColor Yellow
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
