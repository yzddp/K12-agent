# CRON.md — 修远定时任务配置说明书

> 本文件记录所有需要配置的 cron job。**不直接运行**，需要你确认后执行。

## 前置要求

1. 确认 gateway 已启动：`openclaw gateway status`
2. 确认 xiuyuan agent 已注册：`openclaw agents list --bindings`
3. 时区固定为 `Asia/Shanghai`（所有 cron 表达式中已含 --tz）

## Job 概览

| Job | 触发 | 用途 | 必需 |
|-----|------|------|------|
| `xiuyuan-weekly-report` | 每周一 08:00 | 生成周报推送给家长 | ✅ |
| `xiuyuan-monthly-pattern` | 每月 1 日 06:00 | 聚合月度错题画像 | ✅ |
| `xiuyuan-semester-check` | 每 2 个月 1 日 07:00 | 学期/假期模式切换检查 | ✅ |

---

### Job 1: xiuyuan-weekly-report

```
openclaw cron add "0 8 * * 1" ^
  --name xiuyuan-weekly-report ^
  --tz Asia/Shanghai ^
  --session isolated ^
  --agent xiuyuan ^
  --timeout-seconds 300 ^
  --announce ^
  --channel feishu ^
  --to "PARENT_FEISHU_DM_ID" ^
  --message "执行周报生成。按 Standing Orders Order 4 执行。数据来源：error_pattern_index（最新月度）、grade_records（最近 30 天）、tutoring_sessions（最近 7 天）、points_transactions（最近 7 天）。格式纯文本加【】小标题。多孩则汇总所有 child_id。"
```

**注意**：
- 将 `PARENT_FEISHU_DM_ID` 替换为实际家长飞书 chat_id（私聊 ID）
- 如多个家长需推送，可创建多个 job 或统一推送到一个

---

### Job 2: xiuyuan-monthly-pattern

```
openclaw cron add "0 6 1 * *" ^
  --name xiuyuan-monthly-pattern ^
  --tz Asia/Shanghai ^
  --session isolated ^
  --agent xiuyuan ^
  --timeout-seconds 300 ^
  --no-deliver ^
  --message "执行月度错题画像聚合。遍历所有 child_id，从 error_questions 取上月数据，计算总错题数、错误类型分布、薄弱学科、薄弱知识点、进步领域、顽固问题，写入 error_pattern_index 表，period 格式 YYYY-MM。完成后检查 MEMORY.md 是否需要更新摘要。"
```

---

### Job 3: xiuyuan-semester-check

```
openclaw cron add "0 7 1 */2 *" ^
  --name xiuyuan-semester-check ^
  --tz Asia/Shanghai ^
  --session isolated ^
  --agent xiuyuan ^
  --timeout-seconds 180 ^
  --no-deliver ^
  --message "检查学期日历。遍历所有 child_id，查询 semester_calendar 判断当前日期是否处于假期。如进入假期 → 结束当前学习计划、生成假期建议。如假期结束 → 生成收心计划。如学期中 → 不做操作。记录检查结果到 communication_logs。"
```

---

## 执行步骤（手动）

1. 将上面的 `PARENT_FEISHU_DM_ID` 替换为实际值
2. 在 PowerShell 中逐条执行三条 `openclaw cron add` 命令
3. 执行后验证：

```powershell
openclaw cron list
openclaw cron get xiuyuan-weekly-report
openclaw gateway restart
```

4. 复查：

```powershell
openclaw cron list
```

---

## 校验

运行后检查：

- `openclaw cron list` 应显示 3 个 job 都 enabled
- 下次 run 时间正确（周一 08:00 / 每月 1 日 06:00 / 每 2 月 1 日 07:00）
- `openclaw gateway status` 显示 running

---

## 后续维护

- 修改 prompt：**不要用 `openclaw cron edit` CLI ！** 参考 workspace 根 AGENTS.md 的铁律，用 Python 脚本直接写 SQLite，同步更新 `job_json` 和 `payload_message` 两列
- 临时手动触发：`openclaw cron run xiuyuan-weekly-report`
- 删除 job：`openclaw cron remove xiuyuan-weekly-report`
