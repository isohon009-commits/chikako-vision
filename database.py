"""
Baza — har bir tashrif natijasini saqlaydi (SQLite).
Sizning Chikako do'koningizda ham SQLite, shuning uchun tanish.

Jadval: visits — kim, qachon, qaysi do'kon, ball, shubhalimi.
"""

import os
import json
import sqlite3
from datetime import datetime, timezone, timedelta

# O'zbekiston vaqti (UTC+5)
UZ = timezone(timedelta(hours=5))
def now_uz():
    return datetime.now(UZ)

# Ma'lumot saqlanadigan papka.
# Render'da DATA_DIR muhit o'zgaruvchisi diskni ko'rsatadi (saqlanib qoladi).
# Lokalda esa shu papka ishlatiladi.
DATA_DIR = os.environ.get("DATA_DIR", os.path.dirname(__file__))
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "visits.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Jadvalni yaratadi (agar yo'q bo'lsa)."""
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at    TEXT,
            agent         TEXT,
            store         TEXT,
            visit_date    TEXT,
            needs_review  INTEGER,
            flags         TEXT,
            score         INTEGER,
            share         INTEGER,
            facings       INTEGER,
            brand_found   INTEGER,
            real_shelf    INTEGER,
            gps_distance  REAL,
            photo_lat     REAL,
            photo_lng     REAL,
            is_duplicate  INTEGER,
            summary       TEXT
        )
    """)
    conn.commit()

    # Eski bazaga yangi ustunlarni qo'shish (avtomatik migratsiya)
    existing = [r[1] for r in conn.execute("PRAGMA table_info(visits)").fetchall()]
    for col, typ in [("photo_lat", "REAL"), ("photo_lng", "REAL"),
                     ("gps_distance", "REAL"), ("is_duplicate", "INTEGER"),
                     ("photo_file", "TEXT")]:
        if col not in existing:
            conn.execute(f"ALTER TABLE visits ADD COLUMN {col} {typ}")
    conn.commit()
    conn.close()


def save_visit(result, agent="", store="", visit_date="", photo_lat=None, photo_lng=None, photo_file=None):
    """verify_visit() natijasini bazaga yozadi."""
    init_db()
    v = result.get("vision", {})
    gps = result.get("gps") or {}
    dup = result.get("duplicate", {})

    conn = get_conn()
    conn.execute("""
        INSERT INTO visits (created_at, agent, store, visit_date, needs_review,
            flags, score, share, facings, brand_found, real_shelf,
            gps_distance, photo_lat, photo_lng, is_duplicate, summary, photo_file)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        now_uz().strftime("%Y-%m-%d %H:%M"),
        agent, store, visit_date,
        1 if result.get("needs_human_review") else 0,
        json.dumps(result.get("flags", []), ensure_ascii=False),
        v.get("overall_score"),
        v.get("share_of_shelf_percent"),
        v.get("my_brand_facings"),
        1 if v.get("my_brand_found") else 0,
        1 if v.get("is_real_shelf") else 0,
        gps.get("distance_m"),
        photo_lat, photo_lng,
        1 if dup.get("is_duplicate") else 0,
        v.get("summary_uz", ""),
        photo_file,
    ))
    conn.commit()
    conn.close()


def get_visits(only_suspicious=False, agent=None, store=None, date=None):
    """Tashriflar ro'yxatini qaytaradi (eng yangisi birinchi). Filtrlar ixtiyoriy."""
    init_db()
    conn = get_conn()
    q = "SELECT * FROM visits"
    conds, params = [], []
    if only_suspicious:
        conds.append("needs_review = 1")
    if agent:
        conds.append("agent = ?"); params.append(agent)
    if store:
        conds.append("store = ?"); params.append(store)
    if date:
        conds.append("visit_date = ?"); params.append(date)
    if conds:
        q += " WHERE " + " AND ".join(conds)
    q += " ORDER BY id DESC"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["flags"] = json.loads(d["flags"]) if d["flags"] else []
        result.append(d)
    return result


def get_stats(date=None):
    """Statistika. date berilsa, o'sha kun bo'yicha."""
    init_db()
    conn = get_conn()
    where = " WHERE visit_date = ?" if date else ""
    p = (date,) if date else ()
    total = conn.execute("SELECT COUNT(*) FROM visits"+where, p).fetchone()[0]
    suspicious = conn.execute("SELECT COUNT(*) FROM visits"+where+(" AND" if date else " WHERE")+" needs_review = 1", p).fetchone()[0]
    avg_score = conn.execute("SELECT AVG(score) FROM visits"+where, p).fetchone()[0]
    agents = conn.execute("SELECT COUNT(DISTINCT agent) FROM visits"+where, p).fetchone()[0]
    conn.close()
    return {
        "total": total,
        "suspicious": suspicious,
        "clean": total - suspicious,
        "avg_score": round(avg_score, 1) if avg_score else 0,
        "agents": agents,
    }


def get_agents():
    """Barcha agent nomlari (filtr uchun)."""
    init_db()
    conn = get_conn()
    rows = conn.execute("SELECT DISTINCT agent FROM visits WHERE agent != '' ORDER BY agent").fetchall()
    conn.close()
    return [r[0] for r in rows]


# ============== DO'KONLAR BAZASI (A) ==============
def init_stores():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stores (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name  TEXT,
            lat   REAL,
            lng   REAL
        )
    """)
    conn.commit()
    conn.close()


def add_store(name, lat, lng):
    init_stores()
    conn = get_conn()
    conn.execute("INSERT INTO stores (name, lat, lng) VALUES (?,?,?)", (name, lat, lng))
    conn.commit()
    conn.close()


def get_stores():
    init_stores()
    conn = get_conn()
    rows = conn.execute("SELECT * FROM stores ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_store(store_id):
    init_stores()
    conn = get_conn()
    conn.execute("DELETE FROM stores WHERE id = ?", (store_id,))
    conn.commit()
    conn.close()


# ============== AGENT DAVOMATI (C) ==============
def init_attendance():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            agent       TEXT,
            work_date   TEXT,
            start_time  TEXT,
            end_time    TEXT
        )
    """)
    conn.commit()
    conn.close()


def start_work(agent, work_date):
    """Yangi ish seansini boshlaydi. Ochiq seans bo'lsa, o'shani qaytaradi."""
    init_attendance()
    conn = get_conn()
    now = now_uz().strftime("%H:%M")
    # Ochiq (tugatilmagan) seans bormi?
    open_row = conn.execute(
        "SELECT id FROM attendance WHERE agent=? AND work_date=? AND end_time IS NULL",
        (agent, work_date)).fetchone()
    if open_row:
        conn.close()
        return now  # allaqachon ochiq seans bor
    conn.execute("INSERT INTO attendance (agent, work_date, start_time) VALUES (?,?,?)",
                 (agent, work_date, now))
    conn.commit()
    conn.close()
    return now


def end_work(agent, work_date):
    """Eng oxirgi ochiq seansni tugatadi."""
    init_attendance()
    conn = get_conn()
    now = now_uz().strftime("%H:%M")
    row = conn.execute(
        "SELECT id FROM attendance WHERE agent=? AND work_date=? AND end_time IS NULL "
        "ORDER BY id DESC LIMIT 1", (agent, work_date)).fetchone()
    if row:
        conn.execute("UPDATE attendance SET end_time=? WHERE id=?", (now, row["id"]))
        conn.commit()
    conn.close()
    return now


def get_attendance(work_date):
    """Bir kungi davomat: har agent uchun seanslar va do'konlar soni."""
    init_attendance()
    init_db()
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM attendance WHERE work_date=? ORDER BY agent, start_time",
        (work_date,)).fetchall()
    # Agent bo'yicha guruhlash
    by_agent = {}
    for r in rows:
        d = dict(r)
        by_agent.setdefault(d["agent"], []).append(
            {"start_time": d["start_time"], "end_time": d["end_time"]})
    result = []
    for agent, sessions in by_agent.items():
        cnt = conn.execute(
            "SELECT COUNT(DISTINCT store) FROM visits WHERE agent=? AND visit_date=?",
            (agent, work_date)).fetchone()[0]
        result.append({"agent": agent, "sessions": sessions, "stores_visited": cnt})
    conn.close()
    return result


def get_my_visits(agent, work_date):
    """Bitta agentning shu kungi tashriflari (o'zi ko'rishi uchun)."""
    init_db()
    conn = get_conn()
    rows = conn.execute(
        "SELECT store, score, created_at, needs_review FROM visits "
        "WHERE agent=? AND visit_date=? ORDER BY id DESC", (agent, work_date)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def replace_all_stores(rows):
    """Hamma do'konni o'chirib, yangi ro'yxatni yozadi. rows = [(name, lat, lng), ...]"""
    init_stores()
    conn = get_conn()
    conn.execute("DELETE FROM stores")
    conn.executemany("INSERT INTO stores (name, lat, lng) VALUES (?,?,?)", rows)
    conn.commit()
    conn.close()
