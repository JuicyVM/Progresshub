import json
import tkinter as tk
from tkinter import ttk

from .uicommon import button, CANCEL, hline
from .. import i18n, settings as appsettings, theme

LANGUAGES = [("en", "English"), ("es", "Español"), ("fr", "Français")]


class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.app = parent.app
        self.settings = dict(appsettings.load())
        self.title("Settings")
        self.configure(bg=theme.PANEL)
        self.geometry("480x560")
        self.resizable(False, False)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._cancel)

        box = tk.Frame(self, bg=theme.PANEL)
        box.pack(fill="both", expand=True, padx=22, pady=18)

        tk.Label(box, text="SETTINGS", bg=theme.PANEL, fg=theme.ACCENT,
                 font=theme.FONT_T).pack(anchor="w", pady=(0, 14))

        # ------------- LANGUAGE -------------
        tk.Label(box, text=i18n.t("set_lang"), bg=theme.PANEL, fg=theme.MUTED,
                 font=theme.FONT_B).pack(anchor="w", pady=(0, 4))
        self.lang_var = tk.StringVar(value=self.settings.get("lang", "en"))
        lang_row = tk.Frame(box, bg=theme.PANEL)
        lang_row.pack(fill="x", pady=(0, 12))
        for code, label in LANGUAGES:
            tk.Radiobutton(lang_row, text=label, value=code, variable=self.lang_var,
                           bg=theme.PANEL, fg=theme.TEXT, selectcolor=theme.FIELD,
                           activebackground=theme.PANEL, activeforeground=theme.TEXT,
                           font=theme.FONT, relief="flat", bd=0, highlightthickness=0,
                           command=self._preview).pack(side="left", padx=(0, 8))

        # ------------- ACCENT COLOR WHEEL -------------
        tk.Label(box, text=i18n.t("set_accent"), bg=theme.PANEL, fg=theme.MUTED,
                 font=theme.FONT_B).pack(anchor="w", pady=(0, 4))
        wheel = tk.Canvas(box, width=170, height=170, bg=theme.PANEL,
                          highlightthickness=0, bd=0)
        wheel.pack(anchor="w", pady=(0, 8))
        self.wheel = wheel
        self._accent_cache = {}
        self._draw_wheel()
        wheel.bind("<Button-1>", self._pick)
        wheel.bind("<B1-Motion>", self._pick)
        tk.Label(box, text=i18n.t("accent_hint"), bg=theme.PANEL, fg=theme.MUTED,
                 font=theme.FONT_S, wraplength=380, justify="left").pack(
            anchor="w", pady=(0, 10))

        hline(box).pack(fill="x", pady=4)

        presets = [("PROGRESSHUB BLUE", "#7aa2f7"), ("EMBER ORANGE", "#ff9f68"),
                   ("FOREST", "#62de8c"), ("LAVA", "#ff5c72"), ("VIOLET", "#b98bff"),
                   ("TEAL", "#5fd8e8")]
        presel = tk.StringVar(value=self.settings.get("accent") or "")
        row = tk.Frame(box, bg=theme.PANEL)
        row.pack(fill="x", pady=(10, 6))
        for label, hexc in presets:
            cb = tk.Radiobutton(row, value=hexc, variable=presel, bg=theme.PANEL,
                                activebackground=theme.PANEL, relief="flat", bd=0,
                                highlightthickness=0, command=self._preset)
            tk.Label(cb, text="  ", bg=hexc, width=2, height=1, cursor="hand2",
                     relief="raised", bd=	ListBox=0)
            cb.pack(side="left", padx=(0, 2))
            cb.preset_hex = hexc
        self.preset_sel = presel

        tk.Label(box, text=i18n.t("set_theme"), bg=theme.PANEL, fg=theme.MUTED,
                 font=theme.FONT_B).pack(anchor="w", pady=(12, 4))
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
                 wraplength=380, justify="left").pack(anchor="w", pady=(0, 6))

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
        tk.Checkbutton(box, text="Start in fullscreen", variable=self.full_var,
                       bg=theme.PANEL, fg=theme.TEXT, selectcolor=theme.FIELD,
                       activebackground=theme.PANEL, activeforeground=theme.TEXT,
                       font=theme.FONT, relief="flat", bd=0, highlightthickness=0,
                       ).pack(anchor="w", pady=(0, 4))
        tk.Label(box, text="Tip: press F11 to switch fullscreen any time.",
                 bg=theme.PANEL, fg=theme.MUTED, font=theme.FONT_S).pack(anchor="w", pady=(0, 12))

        btn = button(box, i18n.t("set_done"), self._apply, theme.GREEN)
        btn.pack(fill="x", ipady=8)

        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        self.grab_set()

    # ---------------- accent wheel ----------------
    def _hsv_to_rgb(self, h, s, v):
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))

    def _draw_wheel(self):
        w = self.wheel
        size = 170
        cx = cy = size / 2
        R = size / 2 - 6
        for y in range(size):
            for x in range(size):
                dx, dy = x - cx, y - cy
                dist = (dx * dx + dy * dy) ** 0.5
                if dist > R:
                    continue
                ang = (math.atan2(dy, dx) / (2 * math.pi)) % 1.0
                sat = min(dist / R, 1.0)
                key = (round(ang * 30), round(sat * 12), round((y / size) * 12))
                col = self._hsv_to_rgb(ang, sat, 1.0 - (y / size))
                self._accent_cache[key] = col
                if key not in getattr(self, "_wheel_drawn", set()):
                    getattr(self, "_wheel_drawn", set()).add(key)
                    w.create_rectangle(x, y, x + 1, y + 1, fill=col, outline=col)
        # ring + pick dot at current accent
        w.delete("dot")
        cur = self.settings.get("accent") or theme.current_accent()
        r, g, b = theme.hex2rgb(cur)
        import colorsys
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        ang = h * 2 * math.pi
        dist = s * R
        px, py = cx + dist * math.cos(ang), cy + dist * math.sin(ang)
        w.create_oval(px - 4, py - 4, px + 4, py + 4, outline="#ffffff", width=2, tags="dot")

    def _pick(self, event):
        size = 170
        cx = cy = size / 2
        R = size / 2 - 6
        x, y = event.x, event.y
        dx, dy = x - cx, y - cy
        dist = (dx * dx + dy * dy) ** 0.5
        if dist > R + 4:
            return
        import math, colorsys
        if dist < 2:
            ang, sat, val = 0.0, 0.0, 1.0
        else:
            ang = (math.atan2(dy, dx) / (2 * math.pi)) % 1.0
            sat = min(dist / R, 1.0)
            val = 1.0 - (y / size)
        col = self._hsv_to_rgb(ang, sat, val)
        self.settings["accent"] = col
        self._pick_dot(ang, sat, val)
        self._preview()

    def _pick_dot(self, h, s, v):
        size = 170
        cx = cy = size / 2
        R = size / 2 - 6
        ang = h * 2 * math.pi
        px, py = cx + s * R * math.cos(ang), cy + s * R * math.sin(ang)
        self.wheel.delete("dot")
        self.wheel.create_oval(px - 4, py - 4, px + 4, py + 4, outline="#ffffff", width=2, tags="dot")

    def _preset(self):
        self.settings["accent"] = self.preset_sel.get()
        self._preview()

    # ---------------- preview / resolve ----------------
    def _resolve(self, mode):
        import copy
        data = dict(theme.set_theme(mode))
        if self.settings.get("accent"):
            data["accent"] = self.settings["accent"]
        self._resolved = data
        return data

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
        self.settings["ai_key"] = self.ai_key.get().strip()
        self.settings["ai_base"] = self.ai_base.get().strip() or "https://api.openai.com/v1"
        self.settings["ai_model"] = self.ai_model.get().strip() or "gpt-4o-mini"
        self.settings["lang"] = self.lang_var.get()
        i18n.set_lang(self.settings["lang"])
        appsettings.save(self.settings)
        appsettings.apply(self.settings)
        self.app.set_theme(mode, fullscreen=full)
        self.destroy()

    def _cancel(self):
        appsettings.apply(self.app._settings)
        self.destroy()
