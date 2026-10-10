import tkinter as tk
from tkinter import ttk

from .calculator import CalculatorWindow
from .coachui import CoachWindow
from .project import ProjectScreen
from .uicommon import RoundedFrame, button, caption, modal
from .. import db, theme


TYPE_COLORS = {
    "gym": theme.GREEN,
    "trading": theme.ACCENT,
    "weight_loss": theme.ORANGE,
    "calorie": theme.STATUS,
    "sleep": theme.PURPLE,
    "savings": theme.GREEN,
    "study": theme.CYAN,
    "cardio": theme.ORANGE,
    "reading": theme.PURPLE,
    "habits": theme.ACCENT,
}


def type_subtitle(ptype):
    return {
        "gym": "Lifts, PRs, meals",
        "trading": "P/L, win rate, equity",
        "weight_loss": "Weight trend",
        "calorie": "Meals & macros",
        "sleep": "Hours & quality",
        "savings": "Save toward a goal",
        "study": "Subjects & hours",
        "cardio": "Distance & pace",
        "reading": "Books & pages",
        "habits": "Streaks & check-ins",
    }.get(ptype, "")


def quick_stat(project):
    pid = project["id"]
    t = project["ptype"]
    if t == "gym":
        rows = db.gym_sets(pid, limit=100000)
        return ("total volume", f"{sum(r['weight'] * r['reps'] for r in rows):,.0f} kg")
    if t == "trading":
        pnl = sum(t_["pnl"] for t_ in db.trades(pid, limit=100000))
        return ("net P/L", f"{db.currency_symbol(project)}{pnl:+,.0f}")
    if t == "weight_loss":
        rows = db.body_weight(pid)
        return ("current", f"{rows[-1]['weight']:g} kg" if rows else "no data")
    if t == "calorie":
        days = db.daily_calories(pid)
        return ("today", f"{days[-1][1]:,.0f} kcal" if days else "no data")
    if t == "sleep":
        rows = db.simple_rows("sleep_log", pid, limit=100000)
        avg = (sum(r["hours"] for r in rows) / len(rows)) if rows else 0
        return ("avg / night", f"{avg:.1f} h")
    if t == "savings":
        sym = db.currency_symbol(project)
        return ("saved", f"{sym}{db.simple_total('savings_log', pid, 'amount'):,.0f}")
    if t == "study":
        return ("studied", f"{db.simple_total('study_log', pid, 'hours'):,.1f} h")
    if t == "cardio":
        return ("covered", f"{db.simple_total('cardio_log', pid, 'distance'):,.1f} km")
    if t == "reading":
        return ("read", f"{db.simple_total('reading_log', pid, 'pages'):,.0f} pages")
    if t == "habits":
        return ("best streak", f"{db.habit_streak(pid)} days")
    return ("", "")


class DashboardScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app.root, bg=theme.BG)
        self.app = app
        self.pack(fill="both", expand=True)
        try:
            self.winfo_toplevel().after_idle(self._defer_build)
        except Exception:
            self._defer_build()

    def _defer_build(self):
        if not self.winfo_exists():
            return
        self._build()
        self.refresh()

    def _build(self):
        frm = tk.Frame(self, bg=theme.BG)
        frm.pack(fill="both", expand=True, padx=22, pady=18)

        top = tk.Frame(frm, bg=theme.BG)
        top.pack(fill="x", pady=(0, 14))
        tk.Label(top, text=f"Hey, {self.app.user['username'].split()[0].capitalize()} \u2014 what are we tracking today?",
                 bg=theme.BG, fg=theme.TEXT, font=("Segoe UI", 16, "bold")).pack(side="left")
        btn_row = tk.Frame(top, bg=theme.BG)
        btn_row.pack(side="right")
        sett = tk.Label(btn_row, text="\u2699", bg=theme.BG, fg=theme.MUTED, cursor="hand2",
                        font=("Segoe UI", 14))
        sett.pack(side="left", padx=6)
        sett.bind("<Button-1>", lambda e=None: self._open_settings())
        from .uicommon import button
        button(btn_row, "Coach AI", lambda: CoachWindow(self), theme.PURPLE).pack(side="left", padx=3, ipadx=8)
        button(btn_row, "Calculator", lambda: CalculatorWindow(self), theme.CYAN).pack(side="left", padx=3, ipadx=8)
        button(btn_row, "Log out", self.logout, theme.ORANGE).pack(side="left", padx=3, ipadx=8)

        # project-type filter pills
        self._pill_filter = getattr(self, "_pill_filter", "all")
        self.pill_bar = tk.Frame(frm, bg=theme.BG)
        self.pill_bar.pack(fill="x", pady=(0, 10))
        self._build_pills(self._pill_filter)

        body_row = tk.Frame(frm, bg=theme.BG)
        body_row.pack(fill="both", expand=True)

        from .uicommon import ScrollFrame
        holder = ScrollFrame(body_row)
        holder.pack(side="left", fill="both", expand=True)
        self.grid_frame = holder.inner
        self.grid_frame.configure(bg=theme.BG)

        self.promo = tk.Frame(body_row, bg=theme.BG)
        self.promo.pack(side="right", fill="y", padx=(16, 0))
        self._build_promo()

    def _count_projects(self):
        return len(db.list_projects(self.app.user["id"]))

    def _build_promo(self, used=None):
        for w in self.promo.winfo_children():
            w.destroy()
        is_pro = bool(self.app.user.get("is_pro"))
        if used is None:
            used = self._count_projects()
        maxfree = db.FREE_PROJECT_LIMIT
        color = theme.GREEN if is_pro else theme.ACCENT

        card = RoundedFrame(self.promo, height=302, radius=18, fill=theme.PANEL,
                            pad=18, outline=theme.LINE)
        card.pack(fill="both", expand=True)

        accent = tk.Label(card.content, text="PROGRESSHUB", bg=theme.PANEL, fg=theme.MUTED,
                          font=("Segoe UI", 8, "bold")).pack(anchor="w")
        if is_pro:
            tk.Label(card.content, text="PRO ACTIVE", bg=theme.PANEL, fg=theme.GREEN,
                     font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(6, 0))
            tk.Label(card.content, text="Unlimited projects.\nYou're a PRO member.",
                     bg=theme.PANEL, fg=theme.TEXT, font=theme.FONT, justify="left").pack(
                anchor="w", pady=(8, 0))
            self._promo_gauge(card.content, maxfree, maxfree, color)
        else:
            tk.Label(card.content, text="UP TO 5", bg=theme.PANEL, fg=color,
                     font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(2, 0))
            tk.Label(card.content, text="PROJECTS\nFOR FREE", bg=theme.PANEL, fg=theme.TEXT,
                     font=("Segoe UI", 13, "bold")).pack(anchor="w")
            self._used_lbl = tk.Label(card.content, text=f"0/{maxfree} used", bg=theme.PANEL,
                                      fg=theme.MUTED, font=theme.FONT_S)
            self._used_lbl.pack(anchor="w", pady=(12, 4))
            self._promo_gauge(card.content, used, maxfree, color)
            self._promo_countup(self._used_lbl, used)
            button(card.content, "Upgrade to PRO", self._pro_modal, theme.ACCENT).pack(
                fill="x", pady=(14, 0), ipady=7)
            tk.Label(card.content, text="Unlimited projects when subscriptions land.",
                     bg=theme.PANEL, fg=theme.MUTED, font=theme.FONT_S, justify="left",
                     wraplength=140).pack(anchor="w", pady=(10, 0))

    @staticmethod
    def _mix(c1, c2, a):
        def ch(s, i):
            return int(s[i + i*0 + 1:i + i*0 + 3], 16)
        r1, g1, b1 = ch(c1, 1), ch(c1, 3), ch(c1, 5)
        r2, g2, b2 = ch(c2, 1), ch(c2, 3), ch(c2, 5)
        return "#%02x%02x%02x" % tuple(int(x + (y - x) * a) for x, y in ((r1, r2), (g1, g2), (b1, b2)))

    def _promo_pulse(self, bar, color):
        tl = self.winfo_toplevel()
        t0 = __import__("time").monotonic()

        def step():
            if not bar.winfo_exists():
                return
            t = (__import__("time").monotonic() - t0) % 2200 / 2200
            phase = 0.5 - 0.5 * abs(2 * t - 1)
            bar.config(bg=self._mix(color, "#ffffff", phase * 0.45))
            try:
                tl.after(40, step)
            except Exception:
                pass

        step()

    def _promo_countup(self, label, value, ms=700):
        tl = self.winfo_toplevel()
        steps = 30

        def step(i=0):
            if not label.winfo_exists():
                return
            k = min(i / steps, 1.0)
            label.config(text=f"{int((1 - (1 - k) ** 3) * value)}/{db.FREE_PROJECT_LIMIT} used")
            if k < 1.0:
                try:
                    tl.after(int(ms / steps), step, i + 1)
                except Exception:
                    pass

        step()

    def _promo_gauge(self, parent, value, maxv, color):
        bar = tk.Frame(parent, bg=theme.FIELD, height=8, width=140)
        bar.pack(fill="x", pady=(2, 0))
        bar.pack_propagate(False)
        frac = min(value / maxv, 1.0) if maxv else 0
        inner = tk.Frame(bar, bg=color, width=int(140 * frac), height=8)
        inner.place(relheight=1.0)
        self._promo_pulse(inner, color)

    def _pro_modal(self):
        modal(self, "PRO Plan",
              "Subscription is coming soon. Stay tuned!")

    def _set_pill(self, t):
        if getattr(self, "_pill_filter", "all") == t:
            return
        self._pill_filter = t
        self._build_pills(t)
        self.refresh()

    def _build_pills(self, active):
        if getattr(self, "pill_bar", None) is None:
            return
        for w in self.pill_bar.winfo_children():
            w.destroy()
        from .uicommon import RoundedFrame as _P
        from .uicommon import button as _b
        types = [("all", "All")] + list(db.PROJECT_TYPES.items())
        for key, label in types:
            is_on = (key == active)
            fg = theme.TEXT if is_on else theme.MUTED
            bg = theme.ACCENT if is_on else theme.FIELD
            _b(self.pill_bar, label, lambda t=key: self._set_pill(t),
               theme.PURPLE if is_on else theme.FIELD, fg=fg).pack(
                side="left", padx=(0, 6))

    def refresh(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        projs = db.list_projects(self.app.user["id"])
        if getattr(self, "_pill_filter", "all") != "all":
            projs = [p for p in projs if p.get("ptype") == self._pill_filter]
        at_limit = len(projs) >= db.FREE_PROJECT_LIMIT and not self.app.user.get("is_pro")

        for i, p in enumerate(projs):
            card = self._project_card(p)
            card.grid(row=i // 2, column=i % 2, sticky="nsew", padx=6, pady=6)
            self.grid_frame.columnconfigure(0, weight=1)
            self.grid_frame.columnconfigure(1, weight=1)

        if at_limit:
            tile = RoundedFrame(self.grid_frame, height=112, radius=18, fill=theme.FIELD,
                                pad=18, outline=theme.LINE)
            lab = tk.Label(tile.content, text="Pick up PRO\n(unlimited + comes with the subscription)",
                           bg=theme.FIELD, fg=theme.ORANGE, font=("Segoe UI", 10, "bold"),
                           justify="center")
            lab.pack(expand=True)
            lab.bind("<Button-1>", lambda e=None: modal(self, "PRO Plan",
                                                   "Subscription is coming soon. Stay tuned!"))
            n = len(projs)
            tile.grid(row=n // 2, column=n % 2, sticky="nsew", padx=6, pady=6)
        elif len(projs) == 0:
            empty = tk.Frame(self.grid_frame, bg=theme.BG)
            empty.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=40)
            tk.Label(empty, text="No projects yet.", bg=theme.BG, fg=theme.TEXT,
                     font=theme.FONT_T).pack()
            tk.Label(empty, text="Create one below and we'll wire it up for that exact goal.",
                     bg=theme.BG, fg=theme.MUTED, font=theme.FONT).pack(pady=(4, 0))

        # new-project tile
        new = RoundedFrame(self.grid_frame, height=112, radius=18, fill=theme.FIELD,
                           pad=18, outline=theme.LINE)
        new.content.configure(cursor="hand2")
        inner = tk.Frame(new.content, bg=theme.FIELD)
        inner.pack(expand=True)
        plus = tk.Label(inner, text="+", bg=theme.FIELD, fg=theme.MUTED,
                        font=("Segoe UI", 30), cursor="hand2")
        plus.pack()
        tk.Label(inner, text="New project", bg=theme.FIELD, fg=theme.MUTED,
                 font=theme.FONT_B, cursor="hand2").pack()
        for w in (new, new.content, inner, plus):
            w.bind("<Button-1>", lambda e=None: self.new_project())
        n = len(projs)
        new.grid(row=n // 2, column=n % 2, sticky="nsew", padx=6, pady=6)
        self._build_promo(len(projs))

    def _project_card(self, p):
        color = TYPE_COLORS.get(p["ptype"], theme.ACCENT)
        stat, stat_val = quick_stat(p)
        card = RoundedFrame(self.grid_frame, height=112, radius=18, fill=theme.PANEL,
                            pad=18, outline=theme.LINE)
        card.content.bind("<Button-1>", lambda e, pid=p["id"]: self.open_project(pid))

        row0 = tk.Frame(card.content, bg=theme.PANEL)
        row0.pack(fill="x")
        glyph = tk.Label(row0, text=p["name"][0].upper(), bg=color, fg="#11111b",
                         font=("Segoe UI", 13, "bold"), width=3, pady=4)
        glyph.pack(side="left", padx=(0, 10))
        name = tk.Label(row0, text=p["name"], bg=theme.PANEL, fg=theme.TEXT,
                        font=("Segoe UI", 13, "bold"))
        name.pack(side="left")
        del_btn = tk.Label(row0, text="\u00d7", bg=theme.PANEL, fg=theme.MUTED,
                           font=theme.FONT_B, cursor="hand2")
        del_btn.pack(side="right")
        del_btn.bind("<Button-1>", lambda e, pid=p["id"]: self.delete_project(pid))

        tk.Label(card.content, text=f"{db.PROJECT_TYPES.get(p['ptype'], p['ptype'])}  \u00b7  {type_subtitle(p['ptype'])}",
                 bg=theme.PANEL, fg=color, font=theme.FONT_S).pack(anchor="w", pady=(6, 0))
        tk.Label(card.content, text=f"{stat_val}  \u2014  {stat}", bg=theme.PANEL,
                 fg=theme.MUTED, font=theme.FONT_S).pack(anchor="w", pady=(3, 0))
        return card

    def new_project(self):
        win = tk.Toplevel(self)
        win.title("New Project")
        win.configure(bg=theme.PANEL)
        win.resizable(False, False)
        tk.Label(win, text="NEW PROJECT", bg=theme.PANEL, fg=theme.ACCENT,
                 font=theme.FONT_B).pack(anchor="w", padx=22, pady=(16, 4))

        from .uicommon import PlaceholderEntry
        name_e = PlaceholderEntry(win, "Project name (e.g. My Lifts)")
        name_e.pack(padx=22, pady=4, fill="x", ipady=7)

        caption(win, "What are we tracking?", bg=theme.PANEL).pack(anchor="w", padx=22, pady=(10, 2))
        box = tk.Frame(win, bg=theme.PANEL, padx=22)
        box.pack(fill="x")
        combo = ttk.Combobox(box, state="readonly", values=list(db.PROJECT_TYPES.values()),
                             font=theme.FONT)
        combo.pack(fill="x")
        combo.current(0)

        def submit():
            name = name_e.get_value()
            ptype = [k for k, v in db.PROJECT_TYPES.items() if v == combo.get()]
            if ptype:
                ok, res = db.create_project(self.app.user["id"], name, ptype[0])
                if not ok:
                    modal(win, "Can't create", res)
                    return
            win.destroy()
            self.refresh()

        btn = button(win, "Create project", submit, theme.GREEN)
        btn.pack(fill="x", padx=22, pady=14, ipady=8)
        win.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - win.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - win.winfo_height()) // 2
        win.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        win.transient(self)
        win.grab_set()
        name_e.focus_set()

    def delete_project(self, pid, confirm=True):
        db.delete_project(self.app.user["id"], pid)
        self.refresh()

    def open_project(self, pid):
        p = db.get_project(pid)
        if p:
            self.app.show_screen(ProjectScreen, project=p)

    def _open_settings(self):
        from .settingswin import SettingsWindow
        SettingsWindow(self)

    def logout(self):
        from .auth import AuthScreen
        self.app.set_user(None)
        self.app.show_screen(AuthScreen)