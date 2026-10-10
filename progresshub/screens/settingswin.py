import tkinter as tk
from tkinter import ttk

from .uicommon import button, hline
from .. import settings as appsettings
from .. import theme


class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.app = parent.app
        self.settings = dict(appsettings.load())
        self.title("Settings")
        self.configure(bg=theme.PANEL)
        self.geometry("460x480")
        self.resizable(False, False)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._cancel)

        box = tk.Frame(self, bg=theme.PANEL)
        box.pack(fill="both", expand=True, padx=22, pady=18)

        tk.Label(box, text="SETTINGS", bg=theme.PANEL, fg=theme.ACCENT,
                 font=theme.FONT_T).pack(anchor="w", pady=(0, 14))

        tk.Label(box, text="THEME", bg=theme.PANEL, fg=theme.MUTED,
                 font=theme.FONT_B).pack(anchor="w", pady=(0, 4))
        choices = [("system", "System (follow Windows)")] + theme.theme_choices()
        self.values, self.labels = zip(*choices)
        self.theme_var = tk.StringVar(value=self.settings.get("theme", "system"))
        combo = ttk.Combobox(box, textvariable=self.theme_var, values=list(self.labels),
                             state="readonly", font=theme.FONT)
        combo.pack(fill="x")
        combo.current(list(self.values).index(self.theme_var.get())
                      if self.theme_var.get() in self.values else 0)
        combo.bind("<<ComboboxSelected>>", lambda e=None: self._preview())
        self.theme_combo = combo

        self.preview = tk.Frame(box, bg=theme.PANEL)
        self.preview.pack(fill="x", pady=(8, 0))
        self._draw_preview(self._resolve(self.theme_var.get()))

        hline(box).pack(fill="x", pady=12)

        tk.Label(box, text="AI COACH (OPENAI-COMPATIBLE)", bg=theme.PANEL, fg=theme.MUTED,
                 font=theme.FONT_B).pack(anchor="w", pady=(0, 4))
        tk.Label(box, text="Add a key to unlock a real conversational coach. "
                           "Leave blank to use the built-in local coach.",
                 bg=theme.PANEL, fg=theme.MUTED, font=theme.FONT_S,
                 wraplength=390, justify="left").pack(anchor="w", pady=(0, 6))

        self.ai_key = tk.Entry(box, bg=theme.FIELD, fg=theme.TEXT, show="\u2022",
                               insertbackground=theme.TEXT, relief="flat", font=theme.FONT)
        self.ai_key.insert(0, self.settings.get("ai_key", ""))
        self.ai_key.pack(fill="x", ipady=7)
        self.ai_key.bind("<FocusIn>", lambda e=None: self.ai_key.config(show="\u2022"))
        row = tk.Frame(box, bg=theme.PANEL)
        row.pack(fill="x", pady=(6, 0))
        self.ai_base = tk.Entry(row, bg=theme.FIELD, fg=theme.TEXT, insertbackground=theme.TEXT,
                                relief="flat", font=theme.FONT_S)
        self.ai_base.insert(0, self.settings.get("ai_base", "https://api.openai.com/v1"))
        self.ai_base.pack(side="left", fill="x", expand=True, ipady=6)
        self.ai_model = tk.Entry(row, bg=theme.FIELD, fg=theme.TEXT, insertbackground=theme.TEXT,
                                 relief="flat", font=theme.FONT_S, width=13)
        self.ai_model.insert(0, self.settings.get("ai_model", "gpt-4o-mini"))
        self.ai_model.pack(side="left", padx=(6, 0), ipady=6)

        hline(box).pack(fill="x", pady=12)

        self.full_var = tk.BooleanVar(value=bool(self.settings.get("fullscreen", True)))
        tk.Checkbutton(
            box, text="Start in fullscreen", variable=self.full_var,
            bg=theme.PANEL, fg=theme.TEXT, selectcolor=theme.FIELD,
            activebackground=theme.PANEL, activeforeground=theme.TEXT,
            font=theme.FONT, relief="flat", bd=0, highlightthickness=0,
        ).pack(anchor="w", pady=(0, 4))
        tk.Label(box, text="Tip: press F11 to switch fullscreen any time.",
                 bg=theme.PANEL, fg=theme.MUTED, font=theme.FONT_S).pack(anchor="w", pady=(0, 12))

        btn = button(box, "Apply", self._apply, theme.GREEN)
        btn.pack(fill="x", ipady=8)

        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        self.grab_set()

    def _resolve(self, mode):
        return theme.set_theme(mode)

    def _draw_preview(self, data):
        for w in self.preview.winfo_children():
            w.destroy()
        for key in ("accent", "green", "orange", "status", "purple", "cyan"):
            lbl = tk.Label(self.preview, text="Aa", bg=data[key],
                           fg=data["bg" if data["light"] else "text"], font=theme.FONT_B,
                           width=4, pady=4)
            lbl.pack(side="left", padx=(0, 4))

    def _preview(self):
        idx = self.theme_combo.current()
        mode = self.values[idx]
        self._draw_preview(self._resolve(mode))

    def _apply(self):
        idx = self.theme_combo.current()
        mode = self.values[idx]
        full = self.full_var.get()
        self.app._settings["ai_key"] = self.ai_key.get().strip()
        self.app._settings["ai_base"] = self.ai_base.get().strip() or "https://api.openai.com/v1"
        self.app._settings["ai_model"] = self.ai_model.get().strip() or "gpt-4o-mini"
        self.app.set_theme(mode, fullscreen=full)
        self.destroy()

    def _cancel(self):
        appsettings.apply(self.app._settings)
        self.destroy()