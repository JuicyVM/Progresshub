import tkinter as tk

from .uicommon import button, PlaceholderEntry
from .. import db, theme


class AuthScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app.root, bg=theme.BG)
        self.app = app
        self.mode = "login"

        top = tk.Frame(self, bg=theme.BG)
        top.pack(fill="x", pady=14, padx=18)
        sett = tk.Label(top, text="\u2699  Settings", bg=theme.BG, fg=theme.MUTED,
                        font=theme.FONT_B, cursor="hand2")
        sett.pack(side="right")
        sett.bind("<Button-1>", lambda e=None: self._open_settings())

        outer = tk.Frame(self, bg=theme.BG)
        outer.place(relx=0.5, rely=0.5, anchor="center")

        brand = tk.Frame(outer, bg=theme.BG)
        brand.pack(pady=(0, 22))
        dot = tk.Label(brand, text="\u25a0", bg=theme.BG, fg=theme.ACCENT,
                       font=("Segoe UI", 20, "bold"))
        dot.pack(side="left", padx=(0, 8))
        tk.Label(brand, text="ProgressHub", bg=theme.BG, fg=theme.TEXT,
                 font=theme.FONT_XL).pack(side="left")
        tk.Label(outer, text="gym  \u00b7  trading  \u00b7  calories  \u00b7  sleep  \u00b7  savings",
                 bg=theme.BG, fg=theme.MUTED, font=theme.FONT).pack(pady=(0, 10))

        from .uicommon import RoundedFrame
        card = RoundedFrame(outer, height=360, radius=22, fill=theme.PANEL,
                            pad=(30, 24), outline=theme.LINE)
        card.pack()

        tk.Label(card.content, text="WELCOME BACK", bg=theme.PANEL, fg=theme.MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.title_lbl = tk.Label(card.content, text="Log in to your hub",
                                  bg=theme.PANEL, fg=theme.TEXT, font=theme.FONT_T)
        self.title_lbl.pack(anchor="w", pady=(2, 16))

        self.user_e = PlaceholderEntry(card.content, "Username")
        self.user_e.pack(fill="x", ipady=8, pady=(0, 10))
        self.pass_e = PlaceholderEntry(card.content, "Password", show="\u2022")
        self.pass_e.pack(fill="x", ipady=8)

        self.err = tk.Label(card.content, text="", bg=theme.PANEL, fg=theme.ORANGE,
                            font=theme.FONT_S, justify="left", anchor="w", wraplength=280)
        self.err.pack(fill="x", pady=(10, 0))

        for e in (self.user_e, self.pass_e):
            e.bind("<Return>", lambda _e: self.submit())

        self.main_btn = button(card.content, "Log in", self.submit, theme.ACCENT)
        self.main_btn.pack(fill="x", pady=(14, 8), ipady=9)
        self.switch_btn = button(card.content, "New here? Create a free account",
                                 self.toggle, theme.PANEL)
        self.switch_btn.pack(fill="x", ipady=8)

        self.pack(fill="both", expand=True)
        self.user_e.focus_set()

    def _open_settings(self):
        from .settingswin import SettingsWindow
        SettingsWindow(self)

    def toggle(self):
        self.mode = "signup" if self.mode == "login" else "login"
        self.title_lbl.config(text="Create your account" if self.mode == "signup" else "Log in to your hub")
        self.main_btn.config(text="Create account" if self.mode == "signup" else "Log in")
        self.switch_btn.config(
            text="Already have an account? Log in" if self.mode == "signup"
            else "New here? Create a free account"
        )
        self.err.config(text="")

    def submit(self):
        user = self.user_e.get_value()
        pwd = self.pass_e.get_value()
        if self.mode == "login":
            ok, res = db.auth_user(user, pwd)
        else:
            ok, res = db.create_user(user, pwd)
        if not ok:
            self.err.config(text=res)
            return
        self.app.set_user(res)
        from .dashboard import DashboardScreen
        self.app.show_screen(DashboardScreen)