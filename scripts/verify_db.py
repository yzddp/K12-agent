import sqlite3, os

DB = os.path.join(os.environ["USERPROFILE"], ".openclaw", "state", "xiuyuan.db")
conn = sqlite3.connect(DB)
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
print(f"Database: {DB}")
print(f"Tables ({len(tables)}):")
for t in tables:
    cols = conn.execute(f"PRAGMA table_info({t[0]})").fetchall()
    print(f"  {t[0]} ({len(cols)} columns)")
    for c in cols:
        print(f"    - {c[1]} ({c[2]}) {'PK' if c[5] else ''}")
print()
ver = conn.execute("SELECT MAX(version) FROM _schema_version").fetchone()[0]
print(f"Schema version: {ver}")
conn.close()
