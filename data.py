"""
data.py — CSV-backed data layer for TeamFlow CRM.

All data lives in ./data/*.csv so the demo persists within a session and ships
with synthetic sample data (no real people). On first run, if a CSV is missing,
it is seeded from SEED_* below.

Every table is a pandas DataFrame. Helpers load/save and append rows.
"""

import os
import datetime as dt
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

MEMBERS_CSV = os.path.join(DATA_DIR, "members.csv")
METRICS_CSV = os.path.join(DATA_DIR, "metrics.csv")
ONE_ON_ONE_CSV = os.path.join(DATA_DIR, "one_on_ones.csv")
LEAVE_CSV = os.path.join(DATA_DIR, "leave.csv")
TASKS_CSV = os.path.join(DATA_DIR, "tasks.csv")

# ------------------------------------------------------------------ seed data
SEED_MEMBERS = pd.DataFrame([
    {"id": 1, "name": "Aisha Khan",      "role": "Associate",  "tier": "Tier 2", "start_date": "2023-02-14", "email": "aisha.k@example.com",  "status": "Active"},
    {"id": 2, "name": "Diego Santos",    "role": "Associate",  "tier": "Tier 1", "start_date": "2024-06-03", "email": "diego.s@example.com",  "status": "Active"},
    {"id": 3, "name": "Priya Nair",      "role": "SME",        "tier": "Tier 3", "start_date": "2022-09-21", "email": "priya.n@example.com",  "status": "Active"},
    {"id": 4, "name": "Liam O'Brien",    "role": "Associate",  "tier": "Tier 2", "start_date": "2023-11-10", "email": "liam.o@example.com",   "status": "Active"},
    {"id": 5, "name": "Mei Chen",        "role": "Associate",  "tier": "Tier 1", "start_date": "2025-01-20", "email": "mei.c@example.com",    "status": "Active"},
    {"id": 6, "name": "Omar Farouk",     "role": "Team Lead",  "tier": "Tier 3", "start_date": "2021-04-05", "email": "omar.f@example.com",   "status": "Active"},
])

# weekly metrics per member (synthetic). OA% / IR% quality, NRR%, ACHT (sec).
_weeks = ["2026-W36", "2026-W37", "2026-W38", "2026-W39"]
_rows = []
import random as _r
_r.seed(42)
for mid in range(1, 7):
    base_oa = _r.uniform(88, 97)
    base_ir = _r.uniform(85, 96)
    base_nrr = _r.uniform(2, 9)
    base_acht = _r.uniform(380, 620)
    for wk in _weeks:
        _rows.append({
            "member_id": mid, "week": wk,
            "oa_pct": round(base_oa + _r.uniform(-3, 3), 1),
            "ir_pct": round(base_ir + _r.uniform(-3, 3), 1),
            "nrr_pct": round(max(0, base_nrr + _r.uniform(-2, 2)), 1),
            "acht_sec": int(base_acht + _r.uniform(-40, 40)),
        })
SEED_METRICS = pd.DataFrame(_rows)

SEED_ONE_ON_ONES = pd.DataFrame([
    {"id": 1, "member_id": 1, "date": "2026-09-10", "topic": "Quality coaching", "notes": "Reviewed 2 OA misses; agreed to double-check resolution codes.", "action_item": "Shadow Priya on 3 chats", "status": "Open"},
    {"id": 2, "member_id": 2, "date": "2026-09-12", "topic": "Onboarding check-in", "notes": "Settling in well; wants more chat volume.", "action_item": "Increase chat allocation 10%", "status": "Done"},
    {"id": 3, "member_id": 4, "date": "2026-09-15", "topic": "ACHT improvement", "notes": "ACHT trending high on complex cases.", "action_item": "Macros training session", "status": "Open"},
])

SEED_LEAVE = pd.DataFrame([
    {"id": 1, "member_id": 3, "type": "Annual Leave", "start_date": "2026-10-06", "end_date": "2026-10-10", "status": "Approved"},
    {"id": 2, "member_id": 5, "type": "Sick Leave",   "start_date": "2026-09-29", "end_date": "2026-09-30", "status": "Approved"},
    {"id": 3, "member_id": 2, "type": "Annual Leave", "start_date": "2026-10-20", "end_date": "2026-10-24", "status": "Pending"},
])

SEED_TASKS = pd.DataFrame([
    {"id": 1, "title": "Escalation: refund dispute #4471", "assignee_id": 3, "priority": "High",   "due_date": "2026-10-05", "status": "In Progress"},
    {"id": 2, "title": "Weekly QPA coaching logs",          "assignee_id": 6, "priority": "Medium", "due_date": "2026-10-04", "status": "Open"},
    {"id": 3, "title": "NRR audit sample review",           "assignee_id": 1, "priority": "High",   "due_date": "2026-10-03", "status": "Open"},
    {"id": 4, "title": "Update macros doc",                 "assignee_id": 4, "priority": "Low",    "due_date": "2026-10-12", "status": "Done"},
])

_TABLES = {
    MEMBERS_CSV: SEED_MEMBERS, METRICS_CSV: SEED_METRICS,
    ONE_ON_ONE_CSV: SEED_ONE_ON_ONES, LEAVE_CSV: SEED_LEAVE, TASKS_CSV: SEED_TASKS,
}


def _load(csv_path):
    seed = _TABLES[csv_path]
    if not os.path.exists(csv_path):
        seed.to_csv(csv_path, index=False)
        return seed.copy()
    try:
        return pd.read_csv(csv_path)
    except Exception:
        seed.to_csv(csv_path, index=False)
        return seed.copy()


def _save(df, csv_path):
    df.to_csv(csv_path, index=False)


def _next_id(df):
    return int(df["id"].max()) + 1 if len(df) and "id" in df.columns else 1


# ------------------------------------------------------------------ public API
def members():            return _load(MEMBERS_CSV)
def metrics():            return _load(METRICS_CSV)
def one_on_ones():        return _load(ONE_ON_ONE_CSV)
def leave():              return _load(LEAVE_CSV)
def tasks():              return _load(TASKS_CSV)


def member_name(mid):
    m = members()
    row = m[m["id"] == mid]
    return row.iloc[0]["name"] if len(row) else f"#{mid}"


def add_member(name, role, tier, start_date, email, status="Active"):
    df = members()
    new = {"id": _next_id(df), "name": name, "role": role, "tier": tier,
           "start_date": str(start_date), "email": email, "status": status}
    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
    _save(df, MEMBERS_CSV)
    return df


def update_member_status(mid, status):
    df = members()
    df.loc[df["id"] == mid, "status"] = status
    _save(df, MEMBERS_CSV)
    return df


def add_metric(member_id, week, oa_pct, ir_pct, nrr_pct, acht_sec):
    df = metrics()
    new = {"member_id": member_id, "week": week, "oa_pct": oa_pct,
           "ir_pct": ir_pct, "nrr_pct": nrr_pct, "acht_sec": acht_sec}
    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
    _save(df, METRICS_CSV)
    return df


def add_one_on_one(member_id, date, topic, notes, action_item, status="Open"):
    df = one_on_ones()
    new = {"id": _next_id(df), "member_id": member_id, "date": str(date),
           "topic": topic, "notes": notes, "action_item": action_item, "status": status}
    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
    _save(df, ONE_ON_ONE_CSV)
    return df


def add_leave(member_id, ltype, start_date, end_date, status="Pending"):
    df = leave()
    new = {"id": _next_id(df), "member_id": member_id, "type": ltype,
           "start_date": str(start_date), "end_date": str(end_date), "status": status}
    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
    _save(df, LEAVE_CSV)
    return df


def add_task(title, assignee_id, priority, due_date, status="Open"):
    df = tasks()
    new = {"id": _next_id(df), "title": title, "assignee_id": assignee_id,
           "priority": priority, "due_date": str(due_date), "status": status}
    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
    _save(df, TASKS_CSV)
    return df


def set_task_status(task_id, status):
    df = tasks()
    df.loc[df["id"] == task_id, "status"] = status
    _save(df, TASKS_CSV)
    return df
