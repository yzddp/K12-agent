# 修远 — K12 AI 学习辅导员

陪伴孩子完成 K12 全部 12 年学习的 AI 辅导员。基于 OpenClaw Gateway 运行。

## 功能概览

- **辅导答疑** — 苏格拉底式引导，不直接给答案，一次一步
- **错题收集** — 拍照 OCR 录入，结构化沉淀薄弱知识点标签
- **学习计划** — 根据错题和成绩自动生成每日/每周任务
- **成绩追踪** — 成绩录入 + 趋势分析 + 进步/退步报告
- **学期/假期管理** — 自动切换学习模式
- **作文批改** — 语文/英语作文结构化反馈
- **竞赛获奖** — 获奖记录 + 积分联动
- **中考/高考备考** — 倒计时 + 模考分析 + 志愿数据渠道指引
- **积分零花钱系统** — 行为积分自动计算，兑换零花钱
- **家长周报** — 每周一自动推送学情摘要（需配置 cron）
- **多孩子支持** — 一个 workspace 管理多个孩子的独立数据
- **ZPD 自适应** — 语气和提问深度随年级自动调整

## 前置要求

| 依赖 | 版本要求 | 用途 |
|------|----------|------|
| [OpenClaw](https://opencode.ai) | ≥ 2026.4 | AI Gateway 运行环境 |
| Python | ≥ 3.8 | 数据库初始化脚本 |
| 飞书开发者账号 | — | 创建 bot 用于交互 |

OpenClaw 安装：
```powershell
npm install -g openclaw
```

飞书 bot 准备：
1. 在 [飞书开发者后台](https://open.feishu.cn/app) 创建企业自建应用
2. 启用 **机器人** 能力
3. 获取 App ID 和 App Secret（setup 时需要）
4. 配置事件订阅：`im.message.receive_v1`
5. 发布应用并添加到通讯录

## 快速安装

### 方式 A：GitHub 克隆（推荐）

```powershell
git clone https://github.com/YOUR_ORG/workspace-xiuyuan.git
cd workspace-xiuyuan
.\setup.ps1
```

### 方式 B：npm 一键安装

```powershell
npx @openclaw/workspace-xiuyuan
```

底层仍调用 setup.ps1，自动完成所有配置。

升级：

```powershell
# Git 方式
git pull && .\upgrade.ps1

# npm 方式
npx @openclaw/workspace-xiuyuan@latest
```

### setup 脚本会依次：
1. 检测 OpenClaw 是否已安装
2. 询问飞书 bot 的 App ID 和 App Secret
3. 在 openclaw.json 中注册 xiuyuan agent 和飞书 binding
4. 初始化 xiuyuan.db 数据库（18 张表）
5. 提示配置 cron 定时任务（可跳过，后续手动配置）
6. 提示重启 gateway

## 启动

```powershell
openclaw gateway restart
```

## 飞书身份方案

修远使用**同一 bot、双重身份**模式：

| 渠道 | 身份 | 可用功能 |
|------|------|----------|
| 私聊你的 bot | 家长 | 全部功能（初始化/配置/报告/积分管理/兑换确认） |
| 群聊 @bot | 孩子 | 辅导答疑/查积分/查错题/复习 |

家长首次使用需在私聊中完成孩子信息初始化录入。

## 使用场景速查

| 你对 bot 说 | 它会做什么 |
|-------------|-----------|
| "我要设置孩子信息" | 引导录入孩子姓名、年级、教材、课表（仅私聊） |
| "这道题怎么做" | 进入苏格拉底式辅导（仅群聊） |
| "帮我看看这道错题" | 拍照录入，分析错误类型 |
| "制定下周学习计划" | 根据薄弱点生成每日任务 |
| "这次考试考了 85 分" | 记录成绩，分析趋势 |
| "我要换零花钱" | 查积分余额，发起兑换申请 |
| "看周报" | 生成学情报告（仅私聊） |
| "我获奖了" | 录入竞赛获奖，自动加积分 |
| "帮我改作文" | 结构化批改语文/英语作文 |

## 目录结构

```
workspace-xiuyuan/
├── AGENTS.md          # 核心操作规范（所有场景规则）
├── BOOT.md            # Gateway 启动检查清单
├── CRON.md            # 定时任务配置说明书
├── HEARTBEAT.md       # 心跳健康检查
├── IDENTITY.md        # 身份信息和擅长领域
├── MEMORY.md          # 记忆摘要（自动维护）
├── SOUL.md            # 人格设定
├── TOOLS.md           # 工具能力说明
├── USER.md            # 用户画像（含飞书映射）
├── README.md          # 本文件
├── scripts/
│   ├── init_db.py     # 数据库初始化（18 张表）
│   └── verify_db.py   # 数据库结构验证
├── memory/            # 对话记忆存储
└── .openclaw/         # OpenClaw workspace 元数据（自动生成）
```

## 升级

```powershell
# 拉取最新版本
git pull

# 运行升级脚本
.\upgrade.ps1
```

升级脚本会自动更新数据库 schema 并重启 gateway。

## Cron 定时任务（可选）

如需周报自动推送和月度画像聚合，按 CRON.md 执行 3 条 `openclaw cron add` 命令。

## 配置文件参考

安装脚本会自动修改你的 `~/.openclaw/openclaw.json`，添加以下内容：

```json
{
  "agents": {
    "list": [
      {
        "id": "xiuyuan",
        "name": "修远",
        "workspace": "C:\\Users\\YOUR_NAME\\.openclaw\\workspace-xiuyuan",
        "model": { "primary": "minimax/MiniMax-M3" }
      }
    ]
  },
  "bindings": [
    {
      "agentId": "xiuyuan",
      "match": { "channel": "feishu", "accountId": "xiuyuan" }
    }
  ],
  "channels": {
    "feishu": {
      "accounts": {
        "xiuyuan": {
          "appId": "cli_xxx",
          "appSecret": "xxx"
        }
      }
    }
  }
}
```

如需更换模型，将 `model.primary` 改为你支持的 provider/model。

## 发行方案建议

当前提供两种发行方式，按场景选择：

| 方式 | 安装命令 | 升级命令 | 适用场景 |
|------|----------|----------|----------|
| **GitHub 克隆** | `git clone + .\setup.ps1` | `git pull + .\upgrade.ps1` | 开发者、可访问 GitHub |
| **npm 包** | `npx @openclaw/workspace-xiuyuan` | `npx @openclaw/workspace-xiuyuan@latest` | 非技术用户、不需要 git |

**不推荐 pip** 的原因：
- pip 文件写入 site-packages，不适合存放 workspace 配置
- pip 更新会覆盖本地修改，与"用户可自定义"的需求冲突
- 无 postinstall 交互式配置，还需额外脚本

### 推荐：GitHub 仓库 + npm 发布双通道
1. 在 GitHub 托管 `workspace-xiuyuan` 仓库
2. CI 自动发布 npm 包 `@openclaw/workspace-xiuyuan`
3. 用户自主选择安装方式
4. CHANGELOG.md 记录版本变更

### npm 发布步骤

```bash
# 登录 npm
npm login

# 构建并发布
npm publish --access public

# 更新版本
npm version patch  # 或 minor / major
npm publish
```

## 许可

MIT
