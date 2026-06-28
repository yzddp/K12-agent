# BOOT.md — 修远启动检查

Gateway 启动时由 boot-md hook 触发执行。

## 检查清单

### 1. 数据库连接
- 检查 `C:\Users\Administrator\.openclaw\state\xiuyuan.db` 是否存在
- 检查 `_schema_version` 表版本 >= 2
- 确认 16 张表全部存在

### 2. 初始化状态
- 查询 `child_profiles` 是否有记录
- 无记录 → 在 HEARTBEAT.md 写入提醒"等待家长初始化"

### 3. Semester 日历
- 查询 `semester_calendar` 是否有当前学年的记录
- 无记录 → 在 HEARTBEAT.md 写入提醒"请录入学期日历"

### 4. Cron 注册检查
- 确认 3 个 cron job 已注册（非 block 性，仅提醒）

### 5. 待处理事项
- 检查 `study_tasks` 是否有当日 pending 任务
- 检查 `points_redemptions` 是否有未处理的兑换

## 完成

检查通过后回复：`BOOT_OK`
