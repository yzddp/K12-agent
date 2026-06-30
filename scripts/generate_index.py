# -*- coding: utf-8 -*-
"""
从 docs/ 目录扫描所有教材 .md 文件，提取章节结构，生成知识图谱索引。
运行: py scripts/generate_index.py

策略：提取所有 # / ## heading 行，过滤掉通用噪音（封面、目录、版权等），
保留章节、单元、课、练习等作为知识点参考。
"""

import os, re

DOCS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
OUTPUT = os.path.join(DOCS, "知识图谱索引.md")

# 噪音 heading：不包含知识点内容的通用标题
SKIP_HEADINGS = {
    "数学", "语文", "英语", "物理", "化学", "生物", "历史", "地理", "道德与法治",
    "一年级", "二年级", "三年级", "四年级", "五年级", "六年级",
    "七年级", "八年级", "九年级",
    "上册", "下册", "全一册",
    "封面", "封底", "书名", "版权", "编者", "编者的话", "致同学们", "序言",
    "目录", "索引", "后记", "说明", "编写说明",
    "前言", "出版说明", "致读者",
    "ISBN", "定价", "开本", "印张", "字数",
    "义务教育教科书", "普通高中教科书",
    "一年级起点", "三年级起点",
    "图书在版编目", "CIP",
}

# 年级解析
GRADE_ORDER = {
    "一年级": 1, "二年级": 2, "三年级": 3, "四年级": 4, "五年级": 5, "六年级": 6,
    "七年级": 7, "八年级": 8, "九年级": 9,
}

def parse_grade(nianji_dir: str):
    for g in ["一年级","二年级","三年级","四年级","五年级","六年级",
              "七年级","八年级","九年级"]:
        if g in nianji_dir:
            return g, GRADE_ORDER[g]
    if "必修" in nianji_dir:
        return "必修", 10
    if "选择性必修" in nianji_dir or "选修" in nianji_dir:
        return "选择性必修", 11
    return nianji_dir, 99

def extract_chapters(text: str):
    lines = text.split("\n")
    chapters = []
    for line in lines:
        s = line.strip()
        if not s.startswith("# ") and not s.startswith("## "):
            continue
        title = s.lstrip("# ").strip()
        if not title or len(title) > 100:
            continue
        if title in SKIP_HEADINGS:
            continue
        if re.match(r'^\d+$', title):
            continue
        if re.match(r'^第\d+页', title):
            continue
        if re.match(r'^\d{13}$', title):
            continue
        if len(title) < 2:
            continue
        # 过滤"②连一连"这类编号 + 动作指令
        if re.match(r'^[①②③④⑤⑥⑦⑧⑨⑩▪•●○□■]', title):
            continue
        if re.match(r'^\(\d+\)', title):
            continue
        # 过滤纯动作指令
        if title in ("做一做", "摆一摆", "想一想", "说一说", "练一练",
                      "写一写", "算一算", "画一画", "连一连", "涂一涂",
                      "填一填", "比一比", "拼一拼", "议一议", "读一读",
                      "找一找", "看一看", "量一量", "圈一圈", "分一分",
                      "贴一贴", "数一数", "验一验", "试一试"):
            continue
        chapters.append(title)

    seen = set()
    unique = []
    for c in chapters:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique[:30]

def generate():
    xueduan_order = {"小学": 0, "初中": 1, "高中": 2}
    entries = []

    for root, dirs, files in os.walk(DOCS):
        for fname in files:
            if not fname.endswith(".md") or fname == "知识图谱索引.md":
                continue
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, DOCS)
            parts = rel.split(os.sep)
            if len(parts) < 3:
                continue
            xueduan = parts[0]
            if xueduan not in xueduan_order:
                continue
            kemu = parts[1]
            nianji_raw = parts[2] if len(parts) > 2 else ""
            nianji, sort_key = parse_grade(nianji_raw)

            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    text = f.read()
            except:
                continue

            chapters = extract_chapters(text)
            if not chapters:
                continue
            entries.append((xueduan, kemu, sort_key, nianji, fname, rel, chapters))

    entries.sort(key=lambda e: (xueduan_order.get(e[0], 9), e[1], e[2]))

    lines = [
        "# 知识图谱索引",
        "",
        "> 用途：收到批改试卷后，按学科+年级在此索引中检索知识点标签。",
        "> 匹配不到的由 AI 自行总结兜底。",
        "",
    ]

    current_xd = current_km = current_nj = None

    for xd, km, sk, nj, fname, rel, chs in entries:
        if xd != current_xd:
            lines.append(f"## {xd}")
            lines.append("")
            current_xd = xd; current_km = None; current_nj = None
        if km != current_km:
            lines.append(f"### {km}")
            lines.append("")
            current_km = km; current_nj = None
        if nj != current_nj:
            lines.append(f"#### {nj}")
            lines.append("")
            current_nj = nj

        lines.append(f"- `{rel}`")
        for c in chs:
            lines.append(f"  - {c}")
        lines.append("")

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines + [""]))

    print(f"完成: {OUTPUT}")
    print(f"共 {len(entries)} 本教材")

if __name__ == "__main__":
    generate()
