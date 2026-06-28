# USER.md — 用户画像

## 用户结构

### 家长
- 接入方式：飞书私聊 xiuyaun bot
- 身份：关心孩子学业的家长
- 诉求：知道孩子哪里弱、进步了没有、积分数值
- 沟通偏好：直接、有条理、信息密度高
- Feishu parent ID（待初始化时填写）：`ou_df3a92d9416b5eb843fb09b4a4db9da9`

### 孩子（学生）
- 接入方式：飞书群聊 @xiuyaun bot
- 覆盖学段：小学/初中/高三
- 诉求：作业有人辅导、错题有人帮忙分析、查积分
- 沟通偏好：亲切、耐心、不啰嗦

## 多孩子配置

当前活跃 child_id：（待初始化填写）
孩子列表：（每个孩子的 name、child_id、Feishu group_id）

## 积分系统

积分启用：否（待家长初始化确认）
默认汇率：100 分 = 10 元

## Feishu 身份映射

- parent_feishu_id: ou_df3a92d9416b5eb843fb09b4a4db9da9（已在 openclaw.json ownerAllowFrom 注册）
- child_group_ids: （待初始化时添加）

## 沟通规则

- 默认语言：中文
- 时区：中国时区（GMT+8）
- 私聊 = 家长模式：全功能
- 群聊 = 孩子模式：仅辅导/积分查询
- 周报推送：每周一 08:00（家长私聊）
