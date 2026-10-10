import tkinter as tk

from .uicommon import button, section, PlaceholderEntry, ScrollFrame
from .. import calc, theme


class CalculatorWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Calculator")
        self.configure(bg=theme.PANEL)
        self.geometry("440x620")
        self.minsize(380, 420)
        self.resizable(True, True)
        self.transient(parent)

        self._standard()
        self._tools()

        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w = min(self.winfo_width() or 440, sw - 20)
        h = min(self.winfo_height() or 620, sh - 90)
        self.geometry(f"{w}x{h}+{max(sw - w - 18, 0)}+{max(sh - h - 80, 0)}")
        self.grab_set()

    # ---------------------------------------------------------------- standard

    def _standard(self):
        box = tk.Frame(self, bg=theme.PANEL, padx=16)
        box.pack(fill="x", pady=(12, 4))
        tk.Label(box, text="STANDARD", bg=theme.PANEL, fg=theme.MUTED,
                 font=theme.FONT_B).pack(anchor="w")

        self.disp = tk.Entry(box, bg=theme.FIELD, fg=theme.TEXT, insertbackground=theme.TEXT,
                             relief="flat", font=("Segoe UI", 18, "bold"), justify="right")
        self.disp.pack(fill="x", ipady=8, pady=(4, 8))

        keys = [
            "7", "8", "9", "/",
            "4", "5", "6", "*",
            "1", "2", "3", "-",
            "0", ".", "C", "+",
            "(", ")", "sqrt", "=",
        ]
        grid = tk.Frame(box, bg=theme.PANEL)
        grid.pack(fill="x")
        for i, k in enumerate(keys):
            color = theme.ACCENT if k == "=" else theme.GREEN if k == "C" else theme.PANEL
            b = button(grid, k, lambda k=k: self._press(k), color)
            b.grid(row=i // 4, column=i % 4, sticky="nsew", padx=2, pady=2, ipady=8)
            grid.columnconfigure(i % 4, weight=1)
        for r in range(5):
            grid.rowconfigure(r, weight=1)

        self.err = tk.Label(box, text=" Try: 25*4+sqrt(144) ", bg=theme.PANEL, fg=theme.MUTED,
                            font=theme.FONT_S, anchor="w")
        self.err.pack(fill="x", pady=(6, 0))

    def _press(self, key):
        if key == "C":
            self.disp.delete(0, "end")
            self.err.config(text="", fg=theme.MUTED)
            return
        if key == "=":
            self._eval_disp()
            return
        self.disp.insert("end", key)
        self.err.config(text="", fg=theme.MUTED)

    def _eval_disp(self):
        expr = self.disp.get()
        try:
            val = calc.evaluate(expr)
            self.disp.delete(0, "end")
            self.disp.insert(0, f"{val:g}")
        except Exception:
            self.err.config(text="Invalid expression.", fg=theme.ORANGE)

    # ---------------------------------------------------------------- tools

    def _tools(self):
        sc = ScrollFrame(self, bg=theme.PANEL)
        sc.pack(fill="both", expand=True, pady=(4, 12))
        box = tk.Frame(sc.inner, bg=theme.PANEL, padx=16, pady=6)
        box.pack(fill="x")
        section(box, "Quick tools")

        nb = tk.Label(box, text="", bg=theme.PANEL, font=theme.FONT_S)
        nb.pack()

        cal = tk.Frame(box, bg=theme.PANEL)
        cal.pack(fill="x", pady=4)
        tk.Label(cal, text="Calories needed (Mifflin-St Jeor)", bg=theme.PANEL, fg=theme.TEXT,
                 font=theme.FONT_B).pack(anchor="w")
        r = tk.Frame(cal, bg=theme.PANEL)
        r.pack(fill="x")
        self.kg_e = PlaceholderEntry(r, "Weight kg")
        self.kg_e.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.cm_e = PlaceholderEntry(r, "Height cm")
        self.cm_e.pack(side="left", fill="x", expand=True, padx=4)
        self.age_e = PlaceholderEntry(r, "Age")
        self.age_e.pack(side="left", fill="x", expand=True, padx=4)
        self.act_e = PlaceholderEntry(r, "light/active")
        self.act_e.pack(side="left", fill="x", expand=True, padx=(4, 0))
        button(cal, "Go", self._cal, theme.ACCENT).pack(fill="x", pady=(6, 0), ipady=5)
        self.cal_out = tk.Label(cal, text="~2500 kcal/day", bg=theme.PANEL, fg=theme.GREEN,
                                font=theme.FONT_B)
        self.cal_out.pack(anchor="w", pady=(4, 0))

        orm = tk.Frame(box, bg=theme.PANEL)
        orm.pack(fill="x", pady=4)
        tk.Label(orm, text="Est. 1-rep max (Epley)", bg=theme.PANEL, fg=theme.TEXT,
                 font=theme.FONT_B).pack(anchor="w")
        r = tk.Frame(orm, bg=theme.PANEL)
        r.pack(fill="x")
        self.ow_e = PlaceholderEntry(r, "Weight kg")
        self.ow_e.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.or_e = PlaceholderEntry(r, "Reps")
        self.or_e.pack(side="left", fill="x", expand=True, padx=(4, 0))
        button(orm, "Go", self._orm, theme.ACCENT).pack(fill="x", pady=(6, 0), ipady=5)
        self.orm_out = tk.Label(orm, text="~100 kg", bg=theme.PANEL, fg=theme.GREEN,
                                font=theme.FONT_B)
        self.orm_out.pack(anchor="w", pady=(4, 0))

        risk = tk.Frame(box, bg=theme.PANEL)
        risk.pack(fill="x", pady=4)
        tk.Label(risk, text="Position size (risk sizing)", bg=theme.PANEL, fg=theme.TEXT,
                 font=theme.FONT_B).pack(anchor="w")
        r = tk.Frame(risk, bg=theme.PANEL)
        r.pack(fill="x")
        self.acct_e = PlaceholderEntry(r, "Account $")
        self.acct_e.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.risk_e = PlaceholderEntry(r, "Risk %")
        self.risk_e.pack(side="left", fill="x", expand=True, padx=4)
        self.ent_e = PlaceholderEntry(r, "Entry")
        self.ent_e.pack(side="left", fill="x", expand=True, padx=4)
        self.stp_e = PlaceholderEntry(r, "Stop")
        self.stp_e.pack(side="left", fill="x", expand=True, padx=(4, 0))
        button(risk, "Go", self._risk, theme.ACCENT).pack(fill="x", pady=(6, 0), ipady=5)
        self.risk_out = tk.Label(risk, text="0 shares", bg=theme.PANEL, fg=theme.GREEN,
                                 font=theme.FONT_B)
        self.risk_out.pack(anchor="w", pady=(4, 0))

    def _f(self, e):
        try:
            return float(e.get_value())
        except (TypeError, ValueError):
            return None

    def _cal(self):
        w, h, a = self._f(self.kg_e), self._f(self.cm_e), self._f(self.age_e)
        if None in (w, h, a):
            self.cal_out.config(text="Missing values", fg=theme.ORANGE)
            return
        act = (self.act_e.get_value() or "light").lower()
        val = calc.calories_needed(w, h, a, True, act)
        self.cal_out.config(text=f"~{val:,.0f} kcal/day", fg=theme.GREEN)

    def _orm(self):
        w, r = self._f(self.ow_e), self._f(self.or_e)
        if w is None or r is None:
            self.orm_out.config(text="Missing values", fg=theme.ORANGE)
            return
        self.orm_out.config(text=f"~{calc.one_rep_max(w, r):,.0f} kg", fg=theme.GREEN)

    def _risk(self):
        acc, rk, ent, stp = (self._f(self.acct_e), self._f(self.risk_e),
                             self._f(self.ent_e), self._f(self.stp_e))
        if None in (acc, rk, ent, stp):
            self.risk_out.config(text="Missing values", fg=theme.ORANGE)
            return
        try:
            size = calc.risk_size(acc, rk, ent, stp)
            self.risk_out.config(text=f"{size:,.3f} shares  (risk ${acc * rk / 100:,.2f})",
                                 fg=theme.GREEN)
        except ValueError as exc:
            self.risk_out.config(text=str(exc), fg=theme.ORANGE)