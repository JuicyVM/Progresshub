import re
import tkinter as tk
from tkinter import ttk

from .calculator import CalculatorWindow
from .coachui import CoachWindow
from .uicommon import (PlaceholderEntry, RoundedFrame, ScrollFrame, button,
                       caption, stat_card, tree)
from .. import calc, charts, db, theme
from ..db import CURRENCIES


def _f(s):
    if s is None:
        return None
    try:
        return float(re.sub(r"[^\d.\-]", "", str(s)))
    except (TypeError, ValueError):
        return None


def _i(s):
    try:
        return int(s)
    except (TypeError, ValueError):
        return None


def _money(v, project):
    sym = db.currency_symbol(project)
    return f"{sym}{v:+,.2f}"


class TabHost(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=theme.BG)
        self.bar = tk.Frame(self, bg=theme.BG)
        self.bar.pack(fill="x", pady=(0, 12))
        self.stack = tk.Frame(self, bg=theme.BG)
        self.stack.pack(fill="both", expand=True)
        self._tabs = []

    def add(self, title, panel_builder):
        idx = len(self._tabs)
        self._tabs.append(panel_builder(self.stack))
        self._tabs[-1].pack(fill="both", expand=True)
        self._tabs[-1].pack_forget()
        b = tk.Label(self.bar, text=title, bg=theme.FIELD, fg=theme.MUTED, font=theme.FONT_B,
                     padx=16, pady=7, cursor="hand2")
        b.pack(side="left", padx=(0, 8))
        b.bind("<Button-1>", lambda _e, i=idx: self.show(i))
        self._tabs[idx]._btn = b
        if idx == 0:
            self.show(0)

    def show(self, idx):
        for i, t in enumerate(self._tabs):
            t.pack_forget()
            t._btn.config(bg=theme.FIELD, fg=theme.MUTED)
        self._tabs[idx].pack(fill="both", expand=True)
        self._tabs[idx]._btn.config(bg=theme.ACCENT, fg="#11111b")
        refresh = getattr(self._tabs[idx], "refresh", None)
        if refresh:
            refresh()

    def current(self):
        for t in self._tabs:
            if t.winfo_manager():
                return t
        return None


class ProjectScreen(tk.Frame):
    def __init__(self, app, project):
        super().__init__(app.root, bg=theme.BG)
        self.app = app
        self.project = project
        self.pack(fill="both", expand=True)

        head = tk.Frame(self, bg=theme.BG)
        head.pack(fill="x", padx=22, pady=(14, 0))

        nav = tk.Frame(head, bg=theme.BG)
        nav.pack(side="left")
        back = tk.Label(nav, text="\u2190", bg=theme.BG, fg=theme.MUTED, cursor="hand2",
                        font=("Segoe UI", 18, "bold"))
        back.pack(side="left", padx=(0, 10))
        back.bind("<Button-1>", lambda e=None: self._back())
        tk.Label(nav, text=self.project["name"], bg=theme.BG, fg=theme.TEXT,
                 font=("Segoe UI", 19, "bold")).pack(side="left")
        tk.Label(nav, text=f"  \u00b7  {db.PROJECT_TYPES[self.project['ptype']].upper()}",
                 bg=theme.BG, fg=theme.MUTED, font=theme.FONT_S).pack(side="left")

        tools = tk.Frame(head, bg=theme.BG)
        tools.pack(side="right")
        sett = tk.Label(tools, text="\u2699", bg=theme.BG, fg=theme.MUTED, cursor="hand2",
                        font=("Segoe UI", 14))
        sett.pack(side="left", padx=6)
        sett.bind("<Button-1>", lambda e=None: self._open_settings())
        button(tools, "Coach AI", lambda: CoachWindow(self), theme.PURPLE).pack(side="left", padx=3, ipadx=8)
        button(tools, "Calculator", lambda: CalculatorWindow(self), theme.CYAN).pack(side="left", padx=3, ipadx=8)

        wrap = tk.Frame(self, bg=theme.BG)
        wrap.pack(fill="both", expand=True, padx=22, pady=(12, 16))
        self.tabs = TabHost(wrap)
        self.tabs.pack(fill="both", expand=True)

        builders = {
            "gym": [("WORKOUT", _WorkoutPanel), ("BODY WEIGHT", _BodyWeightPanel),
                    ("CALORIES", _MealPanel)],
            "trading": [("LOG TRADE", _TradePanel), ("HISTORY", _TradeHistoryPanel),
                        ("STATS", _TradeStatsPanel)],
            "weight_loss": [("TREND", _WeightPanel)],
            "calorie": [("MEALS", _MealPanel)],
            "sleep": [("LOG", _SimplePanel)],
            "savings": [("LOG", _SimplePanel)],
            "study": [("LOG", _SimplePanel)],
            "cardio": [("LOG", _SimplePanel)],
            "reading": [("LOG", _SimplePanel)],
            "habits": [("CHECK-INS", _SimplePanel)],
        }
        for title, builder in builders.get(self.project["ptype"], []):
            self.tabs.add(title, lambda f, b=builder, t=title: b(f, self.project))

    def _back(self):
        from .dashboard import DashboardScreen
        self.app.show_screen(DashboardScreen)

    def _open_settings(self):
        from .settingswin import SettingsWindow
        SettingsWindow(self)


# ============================================================ generic simple tracker

SIMPLE_CFG = {
    "sleep": {
        "title": "LOG SLEEP", "color": theme.PURPLE, "chart": "HOURS / NIGHT",
        "fields": [("hours", "Hours", "float"), ("note", "Note (optional)", "text")],
        "table": "sleep_log", "value_col": "hours", "mode": "daily", "unit": "h",
    },
    "savings": {
        "title": "LOG A DEPOSIT", "color": theme.GREEN, "chart": "TOTAL SAVED",
        "fields": [("amount", "Amount", "float"), ("note", "Note (optional)", "text")],
        "table": "savings_log", "value_col": "amount", "mode": "cumulative", "unit": "$",
    },
    "study": {
        "title": "LOG A SESSION", "color": theme.CYAN, "chart": "HOURS BY SUBJECT",
        "fields": [("subject", "Subject", "text"), ("hours", "Hours", "float")],
        "table": "study_log", "value_col": "hours", "mode": "subjects", "unit": "h",
    },
    "cardio": {
        "title": "LOG A WORKOUT", "color": theme.ORANGE, "chart": "DISTANCE / DAY",
        "fields": [("activity", "Activity", "text"), ("distance", "Distance (km)", "float"),
                   ("minutes", "Minutes", "int")],
        "table": "cardio_log", "value_col": "distance", "mode": "cumulative", "unit": "km",
    },
    "reading": {
        "title": "LOG READING", "color": theme.PURPLE, "chart": "TOTAL PAGES",
        "fields": [("book", "Book", "text"), ("pages", "Pages read", "int")],
        "table": "reading_log", "value_col": "pages", "mode": "cumulative", "unit": "pgs",
    },
    "habits": {
        "title": "CHECK IN", "color": theme.ACCENT, "chart": "HABITS DONE / DAY",
        "fields": [("habit", "Habit", "text")],
        "table": "habit_log", "value_col": "habit", "mode": "habit", "unit": "",
    },
}


class _SimplePanel(tk.Frame):
    def __init__(self, parent, project):
        super().__init__(parent, bg=theme.BG)
        self.project = project
        self.cfg = SIMPLE_CFG[project["ptype"]]
        self._build()

    def _build(self):
        cfg = self.cfg
        frm = tk.Frame(self, bg=theme.BG)
        frm.pack(fill="both", expand=True)

        fields = cfg["fields"]
        form = RoundedFrame(frm, height=150 if len(fields) <= 1 else 156, radius=16,
                            fill=theme.PANEL, pad=16)
        form.pack(fill="x", pady=(0, 12))
        tk.Label(form.content, text=cfg["title"], bg=theme.PANEL, fg=cfg["color"],
                 font=theme.FONT_B).pack(anchor="w", pady=(0, 10))

        self.fields = {}
        row = tk.Frame(form.content, bg=theme.PANEL)
        row.pack(fill="x")
        for key, label, kind in fields:
            ph = label + (" (h)" if key == "hours" else "")
            e = PlaceholderEntry(row, ph, width=16)
            e.pack(side="left", fill="x", expand=True, padx=(0, 6), ipady=7)
            self.fields[key] = e

        r2 = tk.Frame(form.content, bg=theme.PANEL)
        r2.pack(fill="x", pady=(10, 0))
        self.msg = tk.Label(r2, text="", bg=theme.PANEL, fg=theme.ORANGE, font=theme.FONT_S)
        self.msg.pack(side="left")
        button(r2, "Log it", self._submit, cfg["color"]).pack(side="right", ipadx=16)

        cards = tk.Frame(frm, bg=theme.BG)
        cards.pack(fill="x", pady=(0, 12))
        self._cards = []
        for _ in range(3):
            c = stat_card(cards, "\u2026", "-", cfg["color"], height=76)
            c.pack(side="left", expand=True, fill="x", padx=(0, 8) if not self._cards else (8, 0))
            self._cards.append(c)

        chart_box = RoundedFrame(frm, height=200, radius=16, fill=theme.PANEL, pad=16)
        if cfg["chart"]:
            chart_box.pack(fill="x", pady=(0, 12))
            tk.Label(chart_box.content, text=cfg["chart"], bg=theme.PANEL, fg=theme.MUTED,
                     font=theme.FONT_B).pack(anchor="w", pady=(0, 6))
            self.chart = tk.Canvas(chart_box.content, bg=theme.PANEL, height=140,
                                   highlightthickness=0)
            self.chart.pack(fill="x")

        hist = RoundedFrame(frm, height=286, radius=16, fill=theme.PANEL, pad=16)
        hist.pack(fill="both", expand=True)
        tk.Label(hist.content, text="RECENT", bg=theme.PANEL, fg=theme.MUTED,
                 font=theme.FONT_B).pack(anchor="w", pady=(0, 6))
        cols = ["date"] + [k for k, _, _ in fields]
        self.tree = tree(hist.content, cols, selectmode="browse", height=7)
        self.tree.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(hist.content, command=self.tree.yview, bg=theme.PANEL, bd=0)
        sb.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=sb.set)
        button(hist.content, "Remove selected", self._remove, theme.ORANGE).pack(pady=(8, 0), ipady=5)

    def _submit(self):
        cfg = self.cfg
        values = {"ts": db.today()}
        kinds = {k: knd for k, knd, _ in cfg["fields"]}
        ok = True
        for key, knd in kinds.items():
            raw = self.fields[key].get_value().strip()
            if knd == "text":
                if not raw:
                    ok, values[key] = False, ""
                    break
                values[key] = raw
            elif knd == "float":
                v = _f(raw)
                if v is None or v <= 0:
                    ok = False
                    break
                values[key] = v
            elif knd == "int":
                v = _i(raw)
                if v is None or v < 0:
                    ok = False
                    break
                values[key] = v
        if not ok:
            self.msg.config(text="Fill in the fields.")
            return
        db.log_simple(cfg["table"], self.project["id"], values.pop("ts"), values)
        self.msg.config(text="")
        for e in self.fields.values():
            e.delete(0, "end")
        self.refresh()

    def _remove(self):
        sel = self.tree.selection()
        if not sel:
            return
        row = self._rows[self.tree.index(sel[0])]
        db.delete_simple(self.cfg["table"], self.project["id"], row["id"])
        self.refresh()

    def _series(self):
        cfg = self.cfg
        pid = self.project["id"]
        if cfg["mode"] == "habit":
            return db.habit_series(pid)
        pts = db.simple_series(cfg["table"], pid, cfg["value_col"], limit=120)
        if cfg["mode"] == "cumulative":
            run = 0
            return [(d, (run := run + v)) for d, v in pts]
        if cfg["mode"] == "subjects":
            groups = {}
            for r in db.simple_rows(cfg["table"], pid, limit=100000):
                groups[r.get("subject", "?")] = groups.get(r.get("subject", "?"), 0) + r[cfg["value_col"]]
            return sorted(groups.items(), key=lambda kv: -kv[1])[:12]
        return pts

    def _stats(self):
        cfg = self.cfg
        pid = self.project["id"]
        rows = db.simple_rows(cfg["table"], pid, limit=100000)
        v = cfg["value_col"]
        if cfg["mode"] == "habit":
            done = sum(1 for r in rows if r["done"])
            names = len({r["habit"] for r in rows})
            return [("CURRENT STREAK", f"{db.habit_streak(pid)} d", cfg["color"]),
                    ("CHECK-INS", str(done), theme.GREEN),
                    ("HABITS", str(names), theme.PURPLE)]
        total = sum(r[v] for r in rows)
        if cfg["table"] == "sleep_log":
            avg = total / len(rows) if rows else 0
            best = max((r["hours"] for r in rows), default=0)
            return [("AVG / NIGHT", f"{avg:.1f} h", cfg["color"]),
                    ("NIGHTS", str(len(rows)), theme.GREEN),
                    ("BEST NIGHT", f"{best:g} h", theme.PURPLE)]
        if cfg["table"] == "savings_log":
            sym = db.currency_symbol(self.project)
            biggest = max((r["amount"] for r in rows), default=0)
            return [("TOTAL SAVED", f"{sym}{total:,.0f}", cfg["color"]),
                    ("DEPOSITS", str(len(rows)), theme.GREEN),
                    ("BIGGEST", f"{sym}{biggest:,.0f}", theme.PURPLE)]
        if cfg["table"] == "study_log":
            return [("TOTAL HOURS", f"{total:,.1f}", cfg["color"]),
                    ("SESSIONS", str(len(rows)), theme.GREEN),
                    ("SUBJECTS", str(len({r.get('subject', '?') for r in rows})), theme.PURPLE)]
        if cfg["table"] == "cardio_log":
            best = max((r["distance"] for r in rows), default=0)
            return [("TOTAL DISTANCE", f"{total:,.1f} km", cfg["color"]),
                    ("WORKOUTS", str(len(rows)), theme.GREEN),
                    ("LONGEST", f"{best:g} km", theme.PURPLE)]
        if cfg["table"] == "reading_log":
            books = len({r.get("book", "?") for r in rows})
            return [("TOTAL PAGES", f"{total:,.0f}", cfg["color"]),
                    ("BOOKS", str(books), theme.GREEN),
                    ("SESSIONS", str(len(rows)), theme.PURPLE)]
        return []

    def refresh(self):
        cfg = self.cfg
        stats = self._stats()
        for i, (t, val, col) in enumerate(stats[:3]):
            self._cards[i].set_value(val, col)
        if getattr(self, "chart", None):
            self.chart.update_idletasks()
            charts.draw_line_chart(self.chart, self._series(),
                                   self.chart.winfo_width() or 560, 140, cfg["color"])
        self.tree.delete(*self.tree.get_children())
        self._rows = db.simple_rows(cfg["table"], self.project["id"], limit=80)
        for r in self._rows:
            vals = [r["ts"]]
            for key, _, _ in cfg["fields"]:
                val = r[key]
                if isinstance(val, float):
                    val = f"{val:g}"
                vals.append(val)
            self.tree.insert("", "end", values=vals)


# ============================================================ gym

class _WorkoutPanel(tk.Frame):
    def __init__(self, parent, project):
        super().__init__(parent, bg=theme.BG)
        self.project = project
        self._build()

    def _build(self):
        frm = tk.Frame(self, bg=theme.BG)
        frm.pack(fill="both", expand=True)

        form = RoundedFrame(frm, height=142, radius=16, fill=theme.PANEL, pad=16)
        form.pack(fill="x", pady=(0, 12))
        tk.Label(form.content, text="LOG A SET", bg=theme.PANEL, fg=theme.GREEN,
                 font=theme.FONT_B).pack(anchor="w", pady=(0, 10))
        r1 = tk.Frame(form.content, bg=theme.PANEL)
        r1.pack(fill="x")
        self.date_e = tk.Entry(r1, bg=theme.FIELD, fg=theme.TEXT, insertbackground=theme.TEXT,
                               relief="flat", font=theme.FONT, width=12)
        self.date_e.insert(0, db.today())
        self.date_e.pack(side="left", padx=(0, 6), ipady=7)
        self.ex_e = PlaceholderEntry(r1, "Exercise (e.g. Bench)", width=16)
        self.ex_e.pack(side="left", fill="x", expand=True, padx=6, ipady=7)
        self.wt_e = PlaceholderEntry(r1, "Weight (kg)", width=10)
        self.wt_e.pack(side="left", fill="x", expand=True, padx=6, ipady=7)
        self.rp_e = PlaceholderEntry(r1, "Reps", width=8)
        self.rp_e.pack(side="left", fill="x", expand=True, padx=(6, 0), ipady=7)

        self.msg = tk.Label(form.content, text="", bg=theme.PANEL, fg=theme.ORANGE, font=theme.FONT_S)
        r2 = tk.Frame(form.content, bg=theme.PANEL)
        r2.pack(fill="x", pady=(8, 0))
        button(r2, "Add set", self._submit, theme.GREEN).pack(side="left", ipadx=16)
        button(r2, "Remove selected", self._remove, theme.PANEL).pack(side="left", padx=8, ipadx=10)

        body = tk.Frame(frm, bg=theme.BG)
        body.pack(fill="both", expand=True)
        cards = tk.Frame(body, bg=theme.BG)
        cards.pack(fill="x", pady=(0, 12))
        self.c_total = stat_card(cards, "Total Volume", "-", theme.ACCENT)
        self.c_total.pack(side="left", expand=True, fill="x", padx=(0, 8))
        self.c_sets = stat_card(cards, "Total Sets", "-", theme.GREEN)
        self.c_sets.pack(side="left", expand=True, fill="x", padx=8)
        self.c_days = stat_card(cards, "Workout Days", "-", theme.PURPLE)
        self.c_days.pack(side="left", expand=True, fill="x", padx=(8, 0))

        chart_box = RoundedFrame(body, height=196, radius=16, fill=theme.PANEL, pad=16)
        chart_box.pack(fill="x", pady=(0, 12))
        tk.Label(chart_box.content, text="MONTHLY VOLUME", bg=theme.PANEL, fg=theme.MUTED,
                 font=theme.FONT_B).pack(anchor="w", pady=(0, 6))
        self.chart = tk.Canvas(chart_box.content, bg=theme.PANEL, height=140, highlightthickness=0)
        self.chart.pack(fill="x")

        hist = RoundedFrame(body, height=220, radius=16, fill=theme.PANEL, pad=16)
        hist.pack(fill="both", expand=True)
        tk.Label(hist.content, text="RECENT SETS", bg=theme.PANEL, fg=theme.MUTED,
                 font=theme.FONT_B).pack(anchor="w", pady=(0, 6))
        self.tree = tree(hist.content, ["date", "exercise", "weight", "reps"], selectmode="browse", height=7)
        self.tree.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(hist.content, command=self.tree.yview, bg=theme.PANEL, bd=0)
        sb.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=sb.set)
        self._ids = []

    def _submit(self):
        date = self.date_e.get().strip() or db.today()
        ex = self.ex_e.get_value().strip()
        wt = _f(self.wt_e.get_value())
        rp = _i(self.rp_e.get_value())
        if not ex or wt is None or wt <= 0 or rp is None or rp <= 0:
            self.msg.config(text="Fill exercise, weight and reps.")
            self.msg.pack(anchor="w", pady=(6, 0))
            return
        db.add_gym_set(self.project["id"], date, ex, wt, rp)
        self.msg.pack_forget()
        self.wt_e.delete(0, "end"); self.rp_e.delete(0, "end")
        self.refresh()

    def _remove(self):
        import sqlite3
        sel = self.tree.selection()
        if not sel:
            return
        set_id = self._ids[self.tree.index(sel[0])]["id"]
        con = sqlite3.connect(db.DB_PATH)
        con.execute("DELETE FROM gym_log WHERE id = ?", (set_id,))
        con.commit()
        con.close()
        self.refresh()

    def refresh(self):
        pid = self.project["id"]
        rows = db.gym_sets(pid, limit=100000)
        total = sum(r["weight"] * r["reps"] for r in rows)
        days = len({r["ts"] for r in rows})
        self.c_total.set_value(f"{total:,.0f}")
        self.c_sets.set_value(str(len(rows)))
        self.c_days.set_value(str(days))
        vol = db.gym_weekly_volume(pid)
        self.chart.update_idletasks()
        charts.draw_line_chart(self.chart, [(d, v) for d, v in vol[-10:]],
                               self.chart.winfo_width() or 560, 140, theme.GREEN)
        self.tree.delete(*self.tree.get_children())
        self._ids = []
        for r in db.gym_sets(pid)[:60]:
            self.tree.insert("", "end", values=(r["ts"], r["exercise"], f"{r['weight']:g}", r["reps"]))
            self._ids.append(r)


class _BodyWeightPanel(tk.Frame):
    def __init__(self, parent, project):
        super().__init__(parent, bg=theme.BG)
        self.project = project
        self._build()

    def _build(self):
        frm = tk.Frame(self, bg=theme.BG)
        frm.pack(fill="both", expand=True)
        form = RoundedFrame(frm, height=142, radius=16, fill=theme.PANEL, pad=16)
        form.pack(fill="x", pady=(0, 12))
        tk.Label(form.content, text="LOG BODY WEIGHT", bg=theme.PANEL, fg=theme.ACCENT,
                 font=theme.FONT_B).pack(anchor="w", pady=(0, 8))
        r = tk.Frame(form.content, bg=theme.PANEL)
        r.pack(fill="x")
        self.date_e = tk.Entry(r, bg=theme.FIELD, fg=theme.TEXT, insertbackground=theme.TEXT,
                               relief="flat", font=theme.FONT, width=12)
        self.date_e.insert(0, db.today())
        self.date_e.pack(side="left", padx=(0, 6), ipady=7)
        self.wt_e = PlaceholderEntry(r, "Weight (kg)", width=16)
        self.wt_e.pack(side="left", fill="x", expand=True, padx=(6, 6), ipady=7)
        self.msg = tk.Label(r, text="", bg=theme.PANEL, fg=theme.ORANGE, font=theme.FONT_S)
        self.msg.pack(side="left", padx=8)
        button(form.content, "Log", self._submit, theme.ACCENT).pack(fill="x", pady=(8, 0), ipady=7)

        chart = RoundedFrame(frm, height=248, radius=16, fill=theme.PANEL, pad=16)
        chart.pack(fill="x")
        self.chart = tk.Canvas(chart.content, bg=theme.PANEL, height=216, highlightthickness=0)
        self.chart.pack(fill="x")

    def _submit(self):
        date = self.date_e.get().strip() or db.today()
        wt = _f(self.wt_e.get_value())
        if wt is None or wt <= 0:
            self.msg.config(text="Enter a valid weight.")
            return
        db.add_body_weight(self.project["id"], date, wt)
        self.msg.config(text="")
        self.wt_e.delete(0, "end")
        self.refresh()

    def refresh(self):
        rows = db.body_weight(self.project["id"])
        self.chart.update_idletasks()
        charts.draw_line_chart(self.chart, [(r["ts"], r["weight"]) for r in rows[-20:]],
                               self.chart.winfo_width() or 560, 216, theme.ORANGE)


class _MealPanel(tk.Frame):
    def __init__(self, parent, project):
        super().__init__(parent, bg=theme.BG)
        self.project = project
        self._build()

    def _build(self):
        frm = tk.Frame(self, bg=theme.BG)
        frm.pack(fill="both", expand=True)
        form = RoundedFrame(frm, height=172, radius=16, fill=theme.PANEL, pad=16)
        form.pack(fill="x", pady=(0, 12))
        tk.Label(form.content, text="LOG A MEAL", bg=theme.PANEL, fg=theme.STATUS,
                 font=theme.FONT_B).pack(anchor="w", pady=(0, 8))
        r1 = tk.Frame(form.content, bg=theme.PANEL)
        r1.pack(fill="x")
        self.date_e = tk.Entry(r1, bg=theme.FIELD, fg=theme.TEXT, insertbackground=theme.TEXT,
                               relief="flat", font=theme.FONT, width=12)
        self.date_e.insert(0, db.today())
        self.date_e.pack(side="left", padx=(0, 6), ipady=7)
        self.meal_e = PlaceholderEntry(r1, "Meal (e.g. Chicken rice)", width=16)
        self.meal_e.pack(side="left", fill="x", expand=True, padx=6, ipady=7)
        self.cal_e = PlaceholderEntry(r1, "Calories", width=9)
        self.cal_e.pack(side="left", padx=(6, 0), ipady=7)
        r2 = tk.Frame(form.content, bg=theme.PANEL)
        r2.pack(fill="x", pady=(8, 0))
        self.p_e = PlaceholderEntry(r2, "Protein", width=9)
        self.p_e.pack(side="left", ipady=7)
        self.c_e = PlaceholderEntry(r2, "Carbs", width=9)
        self.c_e.pack(side="left", padx=8, ipady=7)
        self.f_e = PlaceholderEntry(r2, "Fat", width=9)
        self.f_e.pack(side="left", ipady=7)
        self.msg = tk.Label(r2, text="", bg=theme.PANEL, fg=theme.ORANGE, font=theme.FONT_S)
        self.msg.pack(side="left", padx=10)
        b = button(form.content, "Add meal", self._submit, theme.STATUS)
        b.pack(fill="x", pady=(8, 0), ipady=6)

        chart_box = RoundedFrame(frm, height=200, radius=16, fill=theme.PANEL, pad=16)
        chart_box.pack(fill="x", pady=(0, 12))
        tk.Label(chart_box.content, text="DAILY CALORIES", bg=theme.PANEL, fg=theme.MUTED,
                 font=theme.FONT_B).pack(anchor="w", pady=(0, 6))
        self.chart = tk.Canvas(chart_box.content, bg=theme.PANEL, height=130, highlightthickness=0)
        self.chart.pack(fill="x")

        hist = RoundedFrame(frm, height=240, radius=16, fill=theme.PANEL, pad=16)
        hist.pack(fill="both", expand=True)
        tk.Label(hist.content, text="RECENT MEALS", bg=theme.PANEL, fg=theme.MUTED,
                 font=theme.FONT_B).pack(anchor="w", pady=(0, 6))
        self.tree = tree(hist.content, ["date", "meal", "cal"], height=7)
        self.tree.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(hist.content, command=self.tree.yview, bg=theme.PANEL, bd=0)
        sb.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=sb.set)

    def _submit(self):
        date = self.date_e.get().strip() or db.today()
        meal = self.meal_e.get_value().strip()
        cal = _f(self.cal_e.get_value())
        if not meal or cal is None or cal <= 0:
            self.msg.config(text="Meal name + calories needed.")
            return
        db.add_meal(self.project["id"], date, meal, cal,
                    _f(self.p_e.get_value()) or 0,
                    _f(self.c_e.get_value()) or 0,
                    _f(self.f_e.get_value()) or 0)
        self.msg.config(text="")
        self.meal_e.delete(0, "end"); self.cal_e.delete(0, "end")
        self.p_e.delete(0, "end"); self.c_e.delete(0, "end"); self.f_e.delete(0, "end")
        self.refresh()

    def refresh(self):
        pid = self.project["id"]
        by_day = db.daily_calories(pid)
        self.chart.update_idletasks()
        charts.draw_line_chart(self.chart, [(d, c) for d, c in by_day[-14:]],
                               self.chart.winfo_width() or 560, 130, theme.STATUS)
        self.tree.delete(*self.tree.get_children())
        for r in db.meals(pid)[:60]:
            self.tree.insert("", "end", values=(r["ts"], r["meal"], f"{r['calories']:g}"))


# ============================================================ trading

class _TradePanel(tk.Frame):
    def __init__(self, parent, project):
        super().__init__(parent, bg=theme.BG)
        self.project = project
        self._build()

    def _build(self):
        frm = tk.Frame(self, bg=theme.BG)
        frm.pack(fill="both", expand=True)
        form = RoundedFrame(frm, height=200, radius=16, fill=theme.PANEL, pad=16)
        form.pack(fill="x", pady=(0, 12))
        hd = tk.Frame(form.content, bg=theme.PANEL)
        hd.pack(fill="x", pady=(0, 8))
        tk.Label(hd, text="LOG A TRADE", bg=theme.PANEL, fg=theme.ACCENT,
                 font=theme.FONT_B).pack(side="left")
        tk.Label(hd, text="currency", bg=theme.PANEL, fg=theme.MUTED,
                 font=theme.FONT_S).pack(side="left", padx=(10, 4))
        cur_var = tk.StringVar(value=(db.get_project(self.project["id"]) or
                                      self.project).get("currency", "USD"))
        cur = ttk.Combobox(hd, textvariable=cur_var, values=list(CURRENCIES),
                           state="readonly", width=5, font=theme.FONT_S)
        cur.pack(side="left")
        self.cur_var = cur_var
        cur.bind("<<ComboboxSelected>>",
                 lambda e=None: self._set_currency())

        r1 = tk.Frame(form.content, bg=theme.PANEL)
        r1.pack(fill="x")
        self.date_e = tk.Entry(r1, bg=theme.FIELD, fg=theme.TEXT, insertbackground=theme.TEXT,
                               relief="flat", font=theme.FONT, width=12)
        self.date_e.insert(0, db.today())
        self.date_e.pack(side="left", padx=(0, 6), ipady=7)
        self.sym_e = PlaceholderEntry(r1, "Symbol (e.g. AAPL)", width=16)
        self.sym_e.pack(side="left", fill="x", expand=True, padx=6, ipady=7)
        self.side_combo = tk.Label(r1, text="LONG", bg=theme.FIELD, fg=theme.GREEN,
                                   font=theme.FONT_B, padx=14, pady=6, cursor="hand2")
        self.side_combo.pack(side="left", padx=(6, 0))
        self.side_combo.bind("<Button-1>", self._toggle_side)
        self.side = "long"

        r2 = tk.Frame(form.content, bg=theme.PANEL)
        r2.pack(fill="x", pady=(8, 4))
        self.entry_e = PlaceholderEntry(r2, "Entry price", width=10)
        self.entry_e.pack(side="left", ipady=7)
        self.exit_e = PlaceholderEntry(r2, "Exit price", width=10)
        self.exit_e.pack(side="left", padx=8, ipady=7)
        self.qty_e = PlaceholderEntry(r2, "Qty", width=8)
        self.qty_e.pack(side="left", ipady=7)
        self.notes_e = PlaceholderEntry(r2, "Notes (optional)", width=16)
        self.notes_e.pack(side="left", fill="x", expand=True, padx=8, ipady=7)

        self.msg = tk.Label(form.content, text="", bg=theme.PANEL, fg=theme.GREEN, font=theme.FONT_S)
        self.msg.pack(anchor="e")
        b = button(form.content, "Add trade", self._submit, theme.ACCENT)
        b.pack(fill="x", pady=(6, 0), ipady=7)

        hist = RoundedFrame(frm, height=250, radius=16, fill=theme.PANEL, pad=16)
        hist.pack(fill="both", expand=True)
        tk.Label(hist.content, text="RECENT TRADES", bg=theme.PANEL, fg=theme.MUTED,
                 font=theme.FONT_B).pack(anchor="w", pady=(0, 6))
        self.tree = tree(hist.content, ["date", "symbol", "side", "entry", "exit", "qty", "pnl"], height=8)
        self.tree.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(hist.content, command=self.tree.yview, bg=theme.PANEL, bd=0)
        sb.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=sb.set)

    def _toggle_side(self, _e=None):
        self.side = "short" if self.side == "long" else "long"
        self.side_combo.config(text=self.side.upper(),
                               fg=theme.GREEN if self.side == "long" else theme.ORANGE)

    def _set_currency(self):
        code = self.cur_var.get()
        db.set_currency(self.project["id"], code)
        self.project["currency"] = code

    def _submit(self):
        date = self.date_e.get().strip() or db.today()
        sym = self.sym_e.get_value().strip().upper()
        entry = _f(self.entry_e.get_value())
        exit_p = _f(self.exit_e.get_value())
        qty = _f(self.qty_e.get_value())
        if not sym or entry is None or exit_p is None or qty is None or qty <= 0:
            self.msg.config(text="Symbol, entry, exit and qty required.", fg=theme.ORANGE)
            return
        notes = self.notes_e.get_value().strip()
        pnl = db.add_trade(self.project["id"], date, sym, self.side, entry, exit_p, qty, notes)
        self.msg.config(text=f"Added \u00b7 P/L {_money(pnl, self.project)}",
                        fg=theme.GREEN if pnl >= 0 else theme.ORANGE)
        self.sym_e.delete(0, "end"); self.entry_e.delete(0, "end")
        self.exit_e.delete(0, "end"); self.qty_e.delete(0, "end"); self.notes_e.delete(0, "end")
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for r in db.trades(self.project["id"])[:50]:
            pnl = r["pnl"]
            self.tree.insert("", "end", values=(
                r["ts"], r["symbol"], r["direction"].upper(),
                f"{r['entry']:g}", f"{r['exit_p']:g}", f"{r['qty']:g}", _money(pnl, self.project)))
            last = self.tree.get_children()[-1]
            self.tree.tag_configure("w", foreground=theme.GREEN)
            self.tree.tag_configure("l", foreground=theme.ORANGE)
            self.tree.item(last, tags=("w" if pnl >= 0 else "l",))


class _TradeHistoryPanel(tk.Frame):
    def __init__(self, parent, project):
        super().__init__(parent, bg=theme.BG)
        self.project = project
        box = RoundedFrame(self, height=420, radius=16, fill=theme.PANEL, pad=16)
        box.pack(fill="both", expand=True)
        tk.Label(box.content, text="TRADE HISTORY", bg=theme.PANEL, fg=theme.MUTED,
                 font=theme.FONT_B).pack(anchor="w", pady=(0, 6))
        self.tree = tree(box.content, ["date", "symbol", "side", "entry", "exit", "qty", "pnl", "notes"], height=14)
        self.tree.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(box.content, command=self.tree.yview, bg=theme.PANEL, bd=0)
        sb.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=sb.set)
        button(box.content, "Delete selected", self._remove, theme.ORANGE).pack(fill="x", pady=(8, 0), ipady=6)

    def _remove(self):
        import sqlite3
        sel = self.tree.selection()
        if not sel:
            return
        t_id = self._ids[self.tree.index(sel[0])]["id"]
        con = sqlite3.connect(db.DB_PATH)
        con.execute("DELETE FROM trades WHERE id = ?", (t_id,))
        con.commit()
        con.close()
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        self._ids = []
        for r in db.trades(self.project["id"]):
            self.tree.insert("", "end", values=(
                r["ts"], r["symbol"], r["direction"].upper(), f"{r['entry']:g}",
                f"{r['exit_p']:g}", f"{r['qty']:g}", _money(r["pnl"], self.project), r["notes"][:20]))
            self._ids.append(r)


class _TradeStatsPanel(tk.Frame):
    def __init__(self, parent, project):
        super().__init__(parent, bg=theme.BG)
        self.project = project
        self._build()

    def _build(self):
        frm = tk.Frame(self, bg=theme.BG)
        frm.pack(fill="both", expand=True)
        cards = tk.Frame(frm, bg=theme.BG)
        cards.pack(fill="x", pady=(0, 12))
        self.c_net = stat_card(cards, "Net P/L", "-", theme.ACCENT)
        self.c_net.pack(side="left", expand=True, fill="x", padx=(0, 8))
        self.c_wr = stat_card(cards, "Win Rate", "-", theme.GREEN)
        self.c_wr.pack(side="left", expand=True, fill="x", padx=8)
        self.c_pf = stat_card(cards, "Profit Factor", "-", theme.PURPLE)
        self.c_pf.pack(side="left", expand=True, fill="x", padx=(8, 0))

        chart_box = RoundedFrame(frm, height=252, radius=16, fill=theme.PANEL, pad=16)
        chart_box.pack(fill="x")
        tk.Label(chart_box.content, text="EQUITY CURVE", bg=theme.PANEL, fg=theme.MUTED,
                 font=theme.FONT_B).pack(anchor="w", pady=(0, 6))
        self.chart = tk.Canvas(chart_box.content, bg=theme.PANEL, height=190, highlightthickness=0)
        self.chart.pack(fill="x")

    def refresh(self):
        rows = db.trades(self.project["id"])
        pnls = [t["pnl"] for t in rows]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]
        net = sum(pnls)
        wr = len(wins) / len(pnls) * 100 if pnls else 0
        pf = (sum(wins) / abs(sum(losses))) if losses else float("inf")
        self.c_net.set_value(_money(net, self.project), color=theme.GREEN if net >= 0 else theme.ORANGE)
        self.c_wr.set_value(f"{wr:.1f}%")
        self.c_pf.set_value("inf" if pf == float("inf") else f"{pf:.2f}")
        eq = db.equity_curve(self.project["id"])
        self.chart.update_idletasks()
        charts.draw_line_chart(self.chart, eq, self.chart.winfo_width() or 560, 190,
                               theme.GREEN if net >= 0 else theme.ORANGE)


class _WeightPanel(tk.Frame):
    def __init__(self, parent, project):
        super().__init__(parent, bg=theme.BG)
        self.project = project
        self._build()

    def _build(self):
        frm = tk.Frame(self, bg=theme.BG)
        frm.pack(fill="both", expand=True)
        form = RoundedFrame(frm, height=142, radius=16, fill=theme.PANEL, pad=16)
        form.pack(fill="x", pady=(0, 12))
        tk.Label(form.content, text="LOG WEIGHT", bg=theme.PANEL, fg=theme.ORANGE,
                 font=theme.FONT_B).pack(anchor="w", pady=(0, 8))
        r = tk.Frame(form.content, bg=theme.PANEL)
        r.pack(fill="x")
        self.date_e = tk.Entry(r, bg=theme.FIELD, fg=theme.TEXT, insertbackground=theme.TEXT,
                               relief="flat", font=theme.FONT, width=12)
        self.date_e.insert(0, db.today())
        self.date_e.pack(side="left", padx=(0, 6), ipady=7)
        self.wt_e = PlaceholderEntry(r, "Weight (kg)", width=16)
        self.wt_e.pack(side="left", fill="x", expand=True, padx=(6, 6), ipady=7)
        self.msg = tk.Label(r, text="", bg=theme.PANEL, fg=theme.ORANGE, font=theme.FONT_S)
        self.msg.pack(side="left")
        button(form.content, "Log weight", self._submit, theme.ORANGE).pack(fill="x", pady=(8, 0), ipady=7)

        cards = tk.Frame(frm, bg=theme.BG)
        cards.pack(fill="x", pady=(0, 12))
        self.c_start = stat_card(cards, "Start", "-", theme.MUTED, height=70)
        self.c_start.pack(side="left", expand=True, fill="x", padx=(0, 8))
        self.c_now = stat_card(cards, "Current", "-", theme.ORANGE, height=70)
        self.c_now.pack(side="left", expand=True, fill="x", padx=8)
        self.c_delta = stat_card(cards, "Change", "-", theme.GREEN, height=70)
        self.c_delta.pack(side="left", expand=True, fill="x", padx=(8, 0))

        chart = RoundedFrame(frm, height=250, radius=16, fill=theme.PANEL, pad=16)
        chart.pack(fill="both", expand=True)
        self.chart = tk.Canvas(chart.content, bg=theme.PANEL, height=218, highlightthickness=0)
        self.chart.pack(fill="x")

    def _submit(self):
        date = self.date_e.get().strip() or db.today()
        wt = _f(self.wt_e.get_value())
        if wt is None or wt <= 0:
            self.msg.config(text="Enter a valid weight.")
            return
        db.add_body_weight(self.project["id"], date, wt)
        self.msg.config(text="")
        self.wt_e.delete(0, "end")
        self.refresh()

    def refresh(self):
        rows = db.body_weight(self.project["id"])
        if rows:
            first, last = rows[0]["weight"], rows[-1]["weight"]
            self.c_start.set_value(f"{first:g}")
            self.c_now.set_value(f"{last:g}")
            d = last - first
            self.c_delta.set_value(f"{d:+.1f}", color=theme.GREEN if d <= 0 else theme.ORANGE)
        self.chart.update_idletasks()
        charts.draw_line_chart(self.chart, [(r["ts"], r["weight"]) for r in rows[-20:]],
                               self.chart.winfo_width() or 560, 218, theme.ORANGE)