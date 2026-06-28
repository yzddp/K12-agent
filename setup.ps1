<#
.SYNOPSIS
  修远 AI 学习辅导员 — 一键安装脚本
.DESCRIPTION
  注册 xiuyuan agent、配置飞书 bot、初始化数据库、引导 cron 设置
#>

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$OpenClawDir = "$env:USERPROFILE\.openclaw"
$ConfigFile = "$OpenClawDir\openclaw.json"
$AgentId = "xiuyuan"
$AgentName = "修远"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  修远 AI 学习辅导员 — 一键安装" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ---- 步骤 1: 检查前置依赖 ----
Write-Host "[1/6] 检查前置依赖..." -ForegroundColor Yellow

# OpenClaw
try {
    $ocVer = openclaw --version 2>$null
    if (-not $ocVer) { throw "no output" }
    Write-Host "  [OK] OpenClaw: $ocVer" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] 未安装 OpenClaw。请先运行: npm install -g openclaw" -ForegroundColor Red
    exit 1
}

# Python
try {
    $pyVer = py --version 2>&1
    Write-Host "  [OK] Python: $pyVer" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] 未安装 Python 3。请先安装 Python 3.8+" -ForegroundColor Red
    exit 1
}

# openclaw.json 是否存在
if (-not (Test-Path $ConfigFile)) {
    Write-Host "  [FAIL] 未找到 $ConfigFile，请先运行 openclaw 完成初始化" -ForegroundColor Red
    exit 1
}

# ---- 步骤 2: 创建用户配置 ----
Write-Host ""
Write-Host "[2/7] 创建本地用户配置..." -ForegroundColor Yellow
$userFile = "$ScriptDir\USER.md"
$userTemplate = "$ScriptDir\USER.template.md"
if (-not (Test-Path $userFile) -and (Test-Path $userTemplate)) {
    Copy-Item -Path $userTemplate -Destination $userFile
    Write-Host "  [OK] 已从 USER.template.md 创建 USER.md（可安全编辑，不会被 git pull 覆盖）" -ForegroundColor Green
} elseif (Test-Path $userFile) {
    Write-Host "  [OK] USER.md 已存在，保留现有配置" -ForegroundColor Green
} else {
    Write-Host "  [WARN] 未找到 USER.template.md，请手动创建 USER.md" -ForegroundColor Yellow
}

# 检查 MEMORY.md
$memoryFile = "$ScriptDir\MEMORY.md"
if (-not (Test-Path $memoryFile)) {
    "# MEMORY.md — 修远记忆（自动生成）`n`n当前状态：尚无数据" | Out-File -FilePath $memoryFile -Encoding UTF8
    Write-Host "  [OK] 已创建 MEMORY.md 初始模板" -ForegroundColor Green
} else {
    Write-Host "  [OK] MEMORY.md 已存在" -ForegroundColor Green
}

# ---- 步骤 3: 收集飞书配置 ----
Write-Host ""
Write-Host "[3/7] 配置飞书 bot..." -ForegroundColor Yellow

$hasFeishu = Read-Host "是否已有飞书 bot 的 App ID 和 App Secret？(y/n, 默认 y)"
if ($hasFeishu -ne "n") {
    $feishuAppId = Read-Host "  请输入 App ID (如 cli_xxxxxxxxxxxx)"
    $feishuAppSecret = Read-Host "  请输入 App Secret"
    
    # 验证非空
    if ([string]::IsNullOrWhiteSpace($feishuAppId) -or [string]::IsNullOrWhiteSpace($feishuAppSecret)) {
        Write-Host "  [FAIL] App ID 和 App Secret 不能为空" -ForegroundColor Red
        exit 1
    }
    Write-Host "  [OK] 已记录飞书配置" -ForegroundColor Green
} else {
    Write-Host "  [SKIP] 跳过飞书配置，可后续手动修改 openclaw.json" -ForegroundColor Yellow
    $feishuAppId = ""
    $feishuAppSecret = ""
}

# ---- 步骤 4: 注册 agent 和 binding ----
Write-Host ""
Write-Host "[4/7] 注册 agent 到 openclaw.json..." -ForegroundColor Yellow

# 生成绝对 workspace 路径
$wsPath = $ScriptDir

$pythonUpdate = @"
import json, os

cfg_path = r"$($ConfigFile.Replace('\', '\\'))"
ws_path = r"$($wsPath.Replace('\', '\\'))"
agent_id = "$AgentId"
agent_name = "$AgentName"
feishu_id = "$feishuAppId"
feishu_secret = "$feishuAppSecret"

with open(cfg_path, 'r', encoding='utf-8') as f:
    cfg = json.load(f)

# 确保 agents.list 存在
if 'agents' not in cfg:
    cfg['agents'] = {'list': [], 'defaults': {}}
if 'list' not in cfg['agents']:
    cfg['agents']['list'] = []

# 检查是否已注册
existing = [a for a in cfg['agents']['list'] if a.get('id') == agent_id]
if existing:
    print(f"  agent '{agent_id}' 已存在，跳过注册")
else:
    cfg['agents']['list'].append({
        'id': agent_id,
        'name': agent_name,
        'workspace': ws_path,
        'model': {'primary': 'minimax/MiniMax-M3'}
    })
    print(f"  [OK] agent '{agent_id}' 已注册")

# 确保 bindings 存在
if 'bindings' not in cfg:
    cfg['bindings'] = []

existing_bind = [b for b in cfg['bindings'] if b.get('agentId') == agent_id and b.get('match', {}).get('channel') == 'feishu']
if existing_bind:
    print(f"  binding '{agent_id}' → feishu 已存在，跳过")
else:
    cfg['bindings'].append({
        'agentId': agent_id,
        'match': {'channel': 'feishu', 'accountId': agent_id}
    })
    print(f"  [OK] binding '{agent_id}' → feishu 已添加")

# 飞书账号配置
if feishu_id and feishu_secret:
    if 'channels' not in cfg:
        cfg['channels'] = {}
    if 'feishu' not in cfg.get('channels', {}):
        cfg['channels']['feishu'] = {'enabled': True, 'connectionMode': 'websocket', 'dmPolicy': 'pairing', 'accounts': {}}
    if 'accounts' not in cfg['channels']['feishu']:
        cfg['channels']['feishu']['accounts'] = {}
    if feishu_id not in cfg['channels']['feishu']['accounts']:
        cfg['channels']['feishu']['accounts'][agent_id] = {
            'appId': feishu_id,
            'appSecret': feishu_secret
        }
        print(f"  [OK] 飞书账号 '{agent_id}' 已添加")
    else:
        print(f"  飞书账号 '{agent_id}' 已存在，如需更新请手动修改")
    
    # 确保 groups 配置
    if 'groups' not in cfg['channels']['feishu']:
        cfg['channels']['feishu']['groups'] = {'*': {'requireMention': True}}

# 写入
with open(cfg_path, 'w', encoding='utf-8') as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)

print("  [OK] openclaw.json 已更新")
"@

# 写临时 Python 脚本执行
$tmpPy = [System.IO.Path]::GetTempFileName() + ".py"
Set-Content -Path $tmpPy -Value $pythonUpdate -Encoding UTF8
try {
    py $tmpPy
} finally {
    Remove-Item -Force $tmpPy -ErrorAction SilentlyContinue
}

# ---- 步骤 5: 初始化数据库 ----
Write-Host ""
Write-Host "[5/7] 初始化数据库..." -ForegroundColor Yellow
try {
    py "$ScriptDir\scripts\init_db.py"
    Write-Host "  [OK] 数据库初始化完成" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] 数据库初始化失败: $_" -ForegroundColor Red
    exit 1
}

# ---- 步骤 6: Cron 配置引导 ----
Write-Host ""
Write-Host "[6/7] 定时任务配置..." -ForegroundColor Yellow
$setupCron = Read-Host "是否要配置周报等定时任务？(y/n, 默认 n)"
if ($setupCron -eq "y") {
    Write-Host ""
    Write-Host "  请按 CRON.md 中的说明手动执行 cron 命令。" -ForegroundColor White
    Write-Host "  或直接运行: openclaw cron add ...（详见 CRON.md）" -ForegroundColor White
    
    $parentChatId = Read-Host "  请输入家长飞书私聊的 chat_id（用于周报推送，可选）"
    if (-not [string]::IsNullOrWhiteSpace($parentChatId)) {
        Write-Host "  记录 chat_id: $parentChatId" -ForegroundColor Green
        Write-Host "  请在 CRON.md 中将 PARENT_FEISHU_DM_ID 替换为 $parentChatId 后执行" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [SKIP] 可后续按 CRON.md 手动配置" -ForegroundColor Yellow
}

# ---- 步骤 7: 启动与验证 ----
Write-Host ""
Write-Host "[7/7] 启动与验证..." -ForegroundColor Yellow
$restartNow = Read-Host "是否立即重启 Gateway？(y/n, 默认 y)"
if ($restartNow -ne "n") {
    try {
        openclaw gateway restart
        Start-Sleep -Seconds 3
        openclaw gateway status
        Write-Host "  [OK] Gateway 已重启" -ForegroundColor Green
    } catch {
        Write-Host "  [WARN] Gateway 重启命令执行失败，请手动运行: openclaw gateway restart" -ForegroundColor Yellow
    }
} else {
    Write-Host "  请稍后手动重启: openclaw gateway restart" -ForegroundColor Yellow
}

# ---- 完成 ----
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  安装完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步：" -ForegroundColor White
Write-Host "  1. 家长私聊 bot → 说"我要设置孩子信息"开始初始化" -ForegroundColor White
Write-Host "  2. 把孩子拉进群 → @bot 问"这道题怎么做"" -ForegroundColor White
Write-Host "  3. 如需周报自动推送，按 CRON.md 配置 cron" -ForegroundColor White
Write-Host ""
Write-Host "需要帮助？查阅 README.md" -ForegroundColor Cyan
