import hashlib
import os
import secrets
import sqlite3
from datetime import date
from pathlib import Path

DB_PATH = Path(__file__).parent / "progresshub.db"

PROJECT_TYPES = {
    "gym": "Gym & Fitness",
    "trading": "Trading",
    "weight_loss": "Weight Loss",
    "calorie": "Calorie Counter",
    "sleep": "Sleep Tracker",
    "savings": "Savings Goal",
    "study": "Study / Learning",
    "cardio": "Cardio / Running",
    "reading": "Reading",
    "habits": "Habits",
}

FREE_PROJECT_LIMIT = 5

CURRENCIES = {
    "USD": "$", "EUR": "\u20ac", "GBP": "\u00a3", "JPY": "\u00a5", "CAD": "C$",
    "AUD": "A$", "CHF": "Fr", "BRL": "R$", "MXN": "MX$",
    "INR": "\u20b9", "KRW": "\u20a9", "SGD": "S$", "HKD": "HK$", "NZD": "NZ$",
    "CNY": "\u00a5", "TRY": "\u20ba", "PLN": "z\u0142", "SEK": "kr", "NOK": "kr",
    "DKK": "kr", "RUB": "\u20bd", "ZAR": "R", "NGN": "\u20a6", "THB": "\u0e3f",
    "AED": "\u062f.\u0625", "ILS": "\u20aa", "PHP": "\u20b1", "IDR": "Rp",
    "VND": "\u20ab", "ARS": "AR$", "CLP": "CL$", "COP": "CO$", "MYR": "RM",
    "UAH": "\u20b4", "CZK": "K\u010d",
}


def currency_symbol(project):
    return CURRENCIES.get((project or {}).get("currency", "USD"), "$")


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    salt TEXT NOT NULL,
    pw_hash TEXT NOT NULL,
    is_pro INTEGER NOT NULL DEFAULT 0,
    created TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    ptype TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    created TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS gym_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    ts TEXT NOT NULL,
    exercise TEXT NOT NULL,
    weight REAL NOT NULL,
    reps INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS gym_body (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    ts TEXT NOT NULL,
    weight REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS meals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    ts TEXT NOT NULL,
    meal TEXT NOT NULL,
    calories REAL NOT NULL,
    protein REAL DEFAULT 0,
    carbs REAL DEFAULT 0,
    fat REAL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    ts TEXT NOT NULL,
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL,
    entry REAL NOT NULL,
    exit_p REAL NOT NULL,
    qty REAL NOT NULL,
    pnl REAL NOT NULL,
    notes TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS body_weight (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    ts TEXT NOT NULL,
    weight REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS sleep_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    ts TEXT NOT NULL,
    hours REAL NOT NULL,
    note TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS savings_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    ts TEXT NOT NULL,
    amount REAL NOT NULL,
    note TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS study_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    ts TEXT NOT NULL,
    subject TEXT NOT NULL,
    hours REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS cardio_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    ts TEXT NOT NULL,
    activity TEXT NOT NULL,
    distance REAL NOT NULL,
    minutes INTEGER NOT NULL,
    notes TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS reading_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    ts TEXT NOT NULL,
    book TEXT NOT NULL,
    pages INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS habit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    ts TEXT NOT NULL,
    habit TEXT NOT NULL,
    done INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_gym_project ON gym_log(project_id);
CREATE INDEX IF NOT EXISTS idx_gym_body_project ON gym_body(project_id);
CREATE INDEX IF NOT EXISTS idx_meals_project ON meals(project_id);
CREATE INDEX IF NOT EXISTS idx_trades_project ON trades(project_id);
CREATE INDEX IF NOT EXISTS idx_body_weight_project ON body_weight(project_id);
CREATE INDEX IF NOT EXISTS idx_sleep_project ON sleep_log(project_id);
CREATE INDEX IF NOT EXISTS idx_savings_project ON savings_log(project_id);
CREATE INDEX IF NOT EXISTS idx_study_project ON study_log(project_id);
CREATE INDEX IF NOT EXISTS idx_cardio_project ON cardio_log(project_id);
CREATE INDEX IF NOT EXISTS idx_reading_project ON reading_log(project_id);
CREATE INDEX IF NOT EXISTS idx_habit_project ON habit_log(project_id);
CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id);
"""

SIMPLE_TABLES = {
    "sleep_log": {"fields": (("hours", "float"), ("note", "text")), "series": "hours"},
    "savings_log": {"fields": (("amount", "float"), ("note", "text")), "series": "amount"},
    "study_log": {"fields": (("subject", "text"), ("hours", "float")), "series": "hours"},
    "cardio_log": {"fields": (("activity", "text"), ("distance", "float"),
                              ("minutes", "int"), ("notes", "text")), "series": "distance"},
    "reading_log": {"fields": (("book", "text"), ("pages", "int")), "series": "pages"},
    "habit_log": {"fields": (("habit", "text"),), "series": None},
}


def _connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    con = _connect()
    con.executescript(SCHEMA)
    cols = {r["name"] for r in con.execute("PRAGMA table_info(projects)")}
    if "currency" not in cols:
        con.execute("ALTER TABLE projects ADD COLUMN currency TEXT NOT NULL DEFAULT 'USD'")
    con.commit()
    con.close()


def _hash(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 200_000
    ).hex()


def today():
    return date.today().isoformat()


# ---------------------------------------------------------------- auth

def create_user(username, password):
    username = (username or "").strip()
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."
    con = _connect()
    try:
        if con.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone():
            return False, "Username already taken."
        salt = secrets.token_hex(16)
        con.execute(
            "INSERT INTO users (username, salt, pw_hash, is_pro, created) VALUES (?,?,?,?,?)",
            (username, salt, _hash(password, salt), 0, today()),
        )
        con.commit()
        return True, dict(con.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone())
    finally:
        con.close()


def auth_user(username, password):
    username = (username or "").strip()
    con = _connect()
    try:
        row = con.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        if not row:
            return False, "No account with that username. Sign up first."
        if not secrets.compare_digest(row["pw_hash"], _hash(password, row["salt"])):
            return False, "Wrong password."
        return True, dict(row)
    finally:
        con.close()


# ---------------------------------------------------------------- projects

def list_projects(user_id):
    con = _connect()
    try:
        return [dict(r) for r in con.execute(
            "SELECT * FROM projects WHERE user_id = ? ORDER BY created, id", (user_id,)
        )]
    finally:
        con.close()


def get_user(user_id):
    con = _connect()
    try:
        row = con.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None
    finally:
        con.close()


def create_project(user_id, name, ptype):
    name = (name or "").strip()
    if not name:
        return False, "Give the project a name."
    if ptype not in PROJECT_TYPES:
        return False, "Unknown project type."
    con = _connect()
    try:
        user = get_user(user_id)
        count = con.execute(
            "SELECT COUNT(*) AS c FROM projects WHERE user_id = ?", (user_id,)
        ).fetchone()["c"]
        if count >= FREE_PROJECT_LIMIT and not (user and user["is_pro"]):
            return False, f"Free plan caps at {FREE_PROJECT_LIMIT} projects."
        cur = con.execute(
            "INSERT INTO projects (user_id, name, ptype, created) VALUES (?,?,?,?)",
            (user_id, name, ptype, today()),
        )
        con.commit()
        return True, dict(
            con.execute(
                "SELECT * FROM projects WHERE id = ?", (cur.lastrowid,)
            ).fetchone()
        )
    finally:
        con.close()


def delete_project(user_id, project_id):
    con = _connect()
    try:
        con.execute(
            "DELETE FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id)
        )
        for table in ("gym_log", "gym_body", "meals", "trades", "body_weight"):
            con.execute(f"DELETE FROM {table} WHERE project_id = ?", (project_id,))
        con.commit()
        return True
    finally:
        con.close()


def get_project(project_id):
    con = _connect()
    try:
        row = con.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        con.close()


def set_currency(project_id, code):
    code = (code or "USD").upper()
    con = _connect()
    try:
        con.execute("UPDATE projects SET currency = ? WHERE id = ?", (code, project_id))
        con.commit()
    finally:
        con.close()


# ---------------------------------------------------------------- gym

def add_gym_set(project_id, ts, exercise, weight, reps):
    con = _connect()
    try:
        con.execute(
            "INSERT INTO gym_log (project_id, ts, exercise, weight, reps) VALUES (?,?,?,?,?)",
            (project_id, ts, exercise, weight, reps),
        )
        con.commit()
    finally:
        con.close()


def gym_sets(project_id, limit=200):
    con = _connect()
    try:
        return [dict(r) for r in con.execute(
            "SELECT * FROM gym_log WHERE project_id = ? ORDER BY ts DESC, id DESC LIMIT ?",
            (project_id, limit),
        )]
    finally:
        con.close()


def gym_exercises(project_id):
    con = _connect()
    try:
        return [dict(r) for r in con.execute(
            "SELECT exercise, MAX(weight) AS max_weight, COUNT(*) AS sets "
            "FROM gym_log WHERE project_id = ? GROUP BY exercise ORDER BY exercise",
            (project_id,),
        )]
    finally:
        con.close()


def gym_weekly_volume(project_id):
    con = _connect()
    try:
        rows = con.execute(
            "SELECT ts, weight, reps FROM gym_log WHERE project_id = ?", (project_id,)
        ).fetchall()
        weeks = {}
        for r in rows:
            wkey = r["ts"][:7]
            weeks[wkey] = weeks.get(wkey, 0) + r["weight"] * r["reps"]
        return sorted(weeks.items())
    finally:
        con.close()


def body_weight(project_id):
    con = _connect()
    try:
        return [dict(r) for r in con.execute(
            "SELECT * FROM body_weight WHERE project_id = ? ORDER BY ts ASC", (project_id,)
        )]
    finally:
        con.close()


def add_body_weight(project_id, ts, weight):
    con = _connect()
    try:
        con.execute(
            "INSERT INTO body_weight (project_id, ts, weight) VALUES (?,?,?)",
            (project_id, ts, weight),
        )
        con.commit()
    finally:
        con.close()


# ---------------------------------------------------------------- meals

def add_meal(project_id, ts, meal, calories, protein, carbs, fat):
    con = _connect()
    try:
        con.execute(
            "INSERT INTO meals (project_id, ts, meal, calories, protein, carbs, fat) "
            "VALUES (?,?,?,?,?,?,?)",
            (project_id, ts, meal, calories, protein, carbs, fat),
        )
        con.commit()
    finally:
        con.close()


def meals(project_id, limit=300):
    con = _connect()
    try:
        return [dict(r) for r in con.execute(
            "SELECT * FROM meals WHERE project_id = ? ORDER BY ts DESC, id DESC LIMIT ?",
            (project_id, limit),
        )]
    finally:
        con.close()


def daily_calories(project_id):
    con = _connect()
    try:
        rows = con.execute(
            "SELECT ts, SUM(calories) AS cal FROM meals WHERE project_id = ? "
            "GROUP BY ts ORDER BY ts",
            (project_id,),
        ).fetchall()
        return [(r["ts"], r["cal"]) for r in rows]
    finally:
        con.close()


# ---------------------------------------------------------------- trading

def add_trade(project_id, ts, symbol, direction, entry, exit_p, qty, notes):
    pnl = (exit_p - entry) * qty if direction == "long" else (entry - exit_p) * qty
    con = _connect()
    try:
        con.execute(
            "INSERT INTO trades (project_id, ts, symbol, direction, entry, exit_p, qty, pnl, notes) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (project_id, ts, symbol, direction, entry, exit_p, qty, pnl, notes),
        )
        con.commit()
        return pnl
    finally:
        con.close()


def trades(project_id, limit=400):
    con = _connect()
    try:
        return [dict(r) for r in con.execute(
            "SELECT * FROM trades WHERE project_id = ? ORDER BY ts DESC, id DESC LIMIT ?",
            (project_id, limit),
        )]
    finally:
        con.close()


def equity_curve(project_id):
    con = _connect()
    try:
        rows = con.execute(
            "SELECT ts, pnl FROM trades WHERE project_id = ? ORDER BY ts, id", (project_id,)
        ).fetchall()
        running = 0
        points = []
        for r in rows:
            running += r["pnl"]
            points.append((r["ts"], round(running, 2)))
        return points
    finally:
        con.close()


# ---------------------------------------------------------------- generic simple trackers

def _table_cols(table):
    data = SIMPLE_TABLES.get(table)
    if not data:
        raise ValueError(f"Unknown table {table}")
    return {name: kind for name, kind in data["fields"]}


def log_simple(table, project_id, ts, fields):
    cols = _table_cols(table)
    if project_id < 0 or ts == "":
        raise ValueError("bad entry")
    colnames = []
    values = [project_id, ts]
    for name, value in fields.items():
        if name not in cols:
            raise ValueError(f"Unknown column {name}")
        colnames.append(name)
        if cols[name] == "int":
            values.append(int(value))
        elif cols[name] == "float":
            values.append(float(value))
        else:
            values.append(str(value))
    con = _connect()
    try:
        sql = f"INSERT INTO {table} (project_id, ts, {', '.join(colnames)}) VALUES (?,?,{','.join('?' * len(colnames))})"
        con.execute(sql, values)
        con.commit()
        return con.execute("SELECT * FROM %s WHERE project_id = ? ORDER BY id DESC LIMIT 1" % table, (project_id,)).fetchone()
    finally:
        con.close()


def simple_rows(table, project_id, limit=200):
    con = _connect()
    try:
        return [dict(r) for r in con.execute(
            f"SELECT * FROM {table} WHERE project_id = ? ORDER BY ts DESC, id DESC LIMIT ?",
            (project_id, limit),
        )]
    finally:
        con.close()


def simple_series(table, project_id, value_col, limit=90):
    con = _connect()
    try:
        return [(r["ts"], r[value_col]) for r in con.execute(
            f"SELECT ts, {value_col} FROM {table} WHERE project_id = ? ORDER BY ts, id LIMIT ?",
            (project_id, limit),
        )]
    finally:
        con.close()


def delete_simple(table, project_id, entry_id):
    con = _connect()
    try:
        con.execute(f"DELETE FROM {table} WHERE id = ? AND project_id = ?", (entry_id, project_id))
        con.commit()
    finally:
        con.close()


def habit_series(project_id, limit=60):
    con = _connect()
    try:
        rows = con.execute(
            "SELECT ts, COUNT(*) AS done FROM habit_log WHERE project_id = ? AND done = 1 "
            "GROUP BY ts ORDER BY ts LIMIT ?",
            (project_id, limit),
        ).fetchall()
        return [(r["ts"], r["done"]) for r in rows]
    finally:
        con.close()


def habit_streak(project_id, habit=None):
    con = _connect()
    try:
        sql = ("SELECT DISTINCT ts FROM habit_log WHERE project_id = ? AND done = 1"
               + (" AND habit = ?" if habit else ""))
        args = (project_id,) + ((habit,) if habit else ())
        days = sorted(r["ts"] for r in con.execute(sql, args).fetchall())
        if not days:
            return 0
        current = 0
        from datetime import date, timedelta
        seen = set(days)
        d = date.today().isoformat()
        if d not in seen:
            d = (date.fromisoformat(d) - timedelta(days=1)).isoformat() if seen else d
        while d in seen:
            current += 1
            d = (date.fromisoformat(d) - timedelta(days=1)).isoformat()
        return current
    finally:
        con.close()


def simple_total(table, project_id, col):
    con = _connect()
    try:
        row = con.execute(
            f"SELECT COALESCE(SUM({col}),0) AS s FROM {table} WHERE project_id = ?",
            (project_id,),
        ).fetchone()
        return row["s"]
    finally:
        con.close()


def simple_count(table, project_id):
    con = _connect()
    try:
        row = con.execute(
            f"SELECT COUNT(*) AS c FROM {table} WHERE project_id = ?", (project_id,)
        ).fetchone()
        return row["c"]
    finally:
        con.close()