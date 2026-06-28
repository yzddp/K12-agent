# -*- coding: utf-8 -*-
"""
修远数据库初始化脚本 v2
运行方式：py init_db.py
数据库路径见 DB_PATH 变量
"""

import sqlite3, json, os, uuid, datetime

DB_PATH = os.path.join(
    os.environ.get("USERPROFILE", r"C:\Users\Administrator"),
    ".openclaw", "state", "xiuyuan.db"
)

SCHEMA = """

-- 孩子档案
CREATE TABLE IF NOT EXISTS child_profiles (
    child_id        TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    grade           TEXT NOT NULL,
    recorded_date   TEXT NOT NULL,
    textbook_version TEXT NOT NULL,
    current_chapter  TEXT,
    school          TEXT,
    learning_style  TEXT,
    target_school   TEXT,
    target_score    TEXT,
    exam_target     TEXT,                -- 中考/高考/均不
    exam_date       TEXT,
    has_tutor       INTEGER DEFAULT 0,
    study_hours_per_day REAL,
    notes           TEXT,
    adjustment_history TEXT,              -- JSON
    feishu_parent_id TEXT,               -- 家长的 Feishu open_id
    created_at      TEXT DEFAULT (datetime('now','localtime')),
    updated_at      TEXT DEFAULT (datetime('now','localtime'))
);

-- 课表
CREATE TABLE IF NOT EXISTS schedules (
    child_id        TEXT NOT NULL,
    weekday         INTEGER NOT NULL,
    period          INTEGER NOT NULL,
    subject         TEXT NOT NULL,
    textbook_version TEXT,
    current_chapter  TEXT,
    PRIMARY KEY (child_id, weekday, period),
    FOREIGN KEY (child_id) REFERENCES child_profiles(child_id)
);

-- 错题库
CREATE TABLE IF NOT EXISTS error_questions (
    id              TEXT PRIMARY KEY,
    child_id        TEXT NOT NULL,
    subject         TEXT NOT NULL,
    grade           TEXT,
    chapter         TEXT,
    knowledge_tags  TEXT,
    error_type      TEXT,
    error_type_l2   TEXT,
    photo_path      TEXT,
    ocr_text        TEXT,
    student_answer  TEXT,
    teacher_red_mark TEXT,
    ai_summary      TEXT,
    ai_confidence   INTEGER,
    parent_confirmed INTEGER DEFAULT 0,
    created_at      TEXT DEFAULT (datetime('now','localtime')),
    reviewed_count  INTEGER DEFAULT 0,
    mastered        INTEGER DEFAULT 0
);

-- 知识点掌握度
CREATE TABLE IF NOT EXISTS knowledge_mastery (
    child_id        TEXT NOT NULL,
    subject         TEXT NOT NULL,
    knowledge_tag   TEXT NOT NULL,
    mastery_score   INTEGER DEFAULT 0,
    error_count     INTEGER DEFAULT 0,
    last_assessed_at TEXT,
    last_error_at   TEXT,
    trend           TEXT DEFAULT 'stable',
    PRIMARY KEY (child_id, subject, knowledge_tag)
);

-- 成绩记录
CREATE TABLE IF NOT EXISTS grade_records (
    id              TEXT PRIMARY KEY,
    child_id        TEXT NOT NULL,
    exam_name       TEXT,
    exam_type       TEXT,
    exam_date       TEXT,
    subject         TEXT NOT NULL,
    score           REAL,
    full_score      REAL,
    class_rank      INTEGER,
    grade_rank      INTEGER,
    class_avg       REAL,
    grade_avg       REAL
);

-- 学习计划
CREATE TABLE IF NOT EXISTS study_plans (
    id              TEXT PRIMARY KEY,
    child_id        TEXT NOT NULL,
    period          TEXT NOT NULL,
    start_date      TEXT,
    end_date        TEXT,
    subject         TEXT,
    goals           TEXT,
    focus_tags      TEXT,
    status          TEXT DEFAULT 'active',
    created_at      TEXT DEFAULT (datetime('now','localtime'))
);

-- 学习任务
CREATE TABLE IF NOT EXISTS study_tasks (
    id              TEXT PRIMARY KEY,
    child_id        TEXT NOT NULL,
    plan_id         TEXT NOT NULL,
    task_date       TEXT,
    task_type       TEXT,
    content         TEXT,
    estimated_minutes INTEGER,
    status          TEXT DEFAULT 'pending',
    FOREIGN KEY (plan_id) REFERENCES study_plans(id)
);

-- 错题经验画像
CREATE TABLE IF NOT EXISTS error_pattern_index (
    child_id        TEXT NOT NULL,
    period          TEXT NOT NULL,
    total_errors    INTEGER DEFAULT 0,
    error_type_distribution TEXT,
    weak_subjects   TEXT,
    weak_knowledge_tags TEXT,
    improvement_areas TEXT,
    persistent_problems TEXT,
    PRIMARY KEY (child_id, period)
);

-- 情绪观察
CREATE TABLE IF NOT EXISTS mood_logs (
    id              TEXT PRIMARY KEY,
    child_id        TEXT NOT NULL,
    log_date        TEXT,
    mood            TEXT,
    stress_level    INTEGER,
    motivation      INTEGER,
    notes           TEXT
);

-- 辅导对话记录
CREATE TABLE IF NOT EXISTS tutoring_sessions (
    id              TEXT PRIMARY KEY,
    child_id        TEXT NOT NULL,
    subject         TEXT,
    question        TEXT,
    exchange_count  INTEGER DEFAULT 0,
    resolved        INTEGER DEFAULT 0,
    gave_up         INTEGER DEFAULT 0,
    knowledge_tags  TEXT,
    session_start   TEXT,
    session_end     TEXT
);

-- Guardrail 触发日志
CREATE TABLE IF NOT EXISTS guardrail_logs (
    id              TEXT PRIMARY KEY,
    child_id        TEXT NOT NULL,
    session_id      TEXT,
    trigger_type    TEXT,
    content         TEXT,
    triggered_at    TEXT DEFAULT (datetime('now','localtime'))
);

-- 家长沟通记录
CREATE TABLE IF NOT EXISTS communication_logs (
    id              TEXT PRIMARY KEY,
    child_id        TEXT NOT NULL,
    log_date        TEXT DEFAULT (datetime('now','localtime')),
    from_role       TEXT,
    content         TEXT,
    action_items    TEXT
);

-- ==================== v2 新增表 ====================

-- 学期日历
CREATE TABLE IF NOT EXISTS semester_calendar (
    child_id        TEXT NOT NULL,
    year            TEXT NOT NULL,
    semester        TEXT NOT NULL,
    start_date      TEXT NOT NULL,
    end_date        TEXT NOT NULL,
    is_vacation     INTEGER DEFAULT 0,
    label           TEXT,
    PRIMARY KEY (child_id, year, semester),
    FOREIGN KEY (child_id) REFERENCES child_profiles(child_id)
);

-- 获奖记录
CREATE TABLE IF NOT EXISTS awards (
    id              TEXT PRIMARY KEY,
    child_id        TEXT NOT NULL,
    competition_name TEXT NOT NULL,
    competition_level TEXT,
    subject         TEXT,
    award_type      TEXT,
    date            TEXT,
    certificate_path TEXT,
    notes           TEXT,
    created_at      TEXT DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (child_id) REFERENCES child_profiles(child_id)
);

-- 积分配置（家长设置）
CREATE TABLE IF NOT EXISTS points_config (
    child_id        TEXT NOT NULL,
    action_type     TEXT NOT NULL,
    action_label    TEXT NOT NULL,
    points          INTEGER NOT NULL,
    enabled         INTEGER DEFAULT 1,
    PRIMARY KEY (child_id, action_type),
    FOREIGN KEY (child_id) REFERENCES child_profiles(child_id)
);

-- 积分账本（只追加）
CREATE TABLE IF NOT EXISTS points_transactions (
    id              TEXT PRIMARY KEY,
    child_id        TEXT NOT NULL,
    action_type     TEXT NOT NULL,
    delta           INTEGER NOT NULL,
    balance_after   INTEGER NOT NULL,
    reason          TEXT,
    source          TEXT DEFAULT 'auto',
    created_at      TEXT DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (child_id) REFERENCES child_profiles(child_id)
);

-- 兑换记录
CREATE TABLE IF NOT EXISTS points_redemptions (
    id              TEXT PRIMARY KEY,
    child_id        TEXT NOT NULL,
    points_spent    INTEGER NOT NULL,
    rmb_amount      REAL NOT NULL,
    requested_at    TEXT DEFAULT (datetime('now','localtime')),
    approved_at     TEXT,
    paid            INTEGER DEFAULT 0,
    FOREIGN KEY (child_id) REFERENCES child_profiles(child_id)
);

-- ==================== schema 版本 ====================

CREATE TABLE IF NOT EXISTS _schema_version (
    version         INTEGER PRIMARY KEY,
    applied_at      TEXT DEFAULT (datetime('now','localtime'))
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_error_child ON error_questions(child_id);
CREATE INDEX IF NOT EXISTS idx_error_created ON error_questions(created_at);
CREATE INDEX IF NOT EXISTS idx_mastery_child ON knowledge_mastery(child_id);
CREATE INDEX IF NOT EXISTS idx_grade_child ON grade_records(child_id);
CREATE INDEX IF NOT EXISTS idx_session_child ON tutoring_sessions(child_id);
CREATE INDEX IF NOT EXISTS idx_schedule_child ON schedules(child_id);
CREATE INDEX IF NOT EXISTS idx_plan_child ON study_plans(child_id);
CREATE INDEX IF NOT EXISTS idx_mood_child ON mood_logs(child_id);
CREATE INDEX IF NOT EXISTS idx_pattern_child ON error_pattern_index(child_id);
CREATE INDEX IF NOT EXISTS idx_award_child ON awards(child_id);
CREATE INDEX IF NOT EXISTS idx_points_child ON points_transactions(child_id);
CREATE INDEX IF NOT EXISTS idx_calendar_child ON semester_calendar(child_id);
"""

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    conn.executescript(SCHEMA)

    # 对已存在的旧表执行 ALTER TABLE 追加 v2 字段
    existing = {t[0] for t in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}

    if "child_profiles" in existing:
        for col in ("exam_target", "exam_date", "feishu_parent_id"):
            try:
                cur.execute(f"ALTER TABLE child_profiles ADD COLUMN {col} TEXT")
            except Exception:
                pass  # 已存在则跳过

    if "guardrail_logs" in existing:
        try:
            cur.execute("ALTER TABLE guardrail_logs ADD COLUMN child_id TEXT NOT NULL DEFAULT 'unknown'")
        except Exception:
            pass

    if "study_tasks" in existing:
        try:
            cur.execute("ALTER TABLE study_tasks ADD COLUMN child_id TEXT NOT NULL DEFAULT 'unknown'")
        except Exception:
            pass

    # 确保版本号记录
    cur.execute("INSERT OR IGNORE INTO _schema_version (version) VALUES (2)")
    conn.commit()
    conn.close()
    print(f"数据库已初始化: {DB_PATH}")

if __name__ == "__main__":
    init_db()
