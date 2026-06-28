# HEARTBEAT.md — 修远心跳检查

## 正常状态

如果一切正常，回复：`HEARTBEAT_OK`

## 检查清单

1. 是否有待处理的家长确认请求？（points_redemptions 中 paid=0）
2. 本周周报是否已生成？
3. 是否有连续 3 次以上学生放弃记录？（tutoring_sessions.gave_up）
4. 各 session 是否正常结束？
5. 当天是否有 pending 的学习任务？（study_tasks WHERE status='pending' AND task_date=today）
6. 是否有积分篡改尝试记录？（guardrail_logs WHERE trigger_type='points_tamper_attempt'）
7. 是否需要学期/假期模式切换？（检查 semester_calendar）
8. 数据库 schema 版本是否 >= 2？

## 待初始化提醒

- 如 child_profiles 无记录：回复中包含"⚠️ 尚未初始化，请家长私聊录入孩子信息"
- 如 semester_calendar 无记录：回复中包含"⚠️ 未录入学期日历，请家长补充"
