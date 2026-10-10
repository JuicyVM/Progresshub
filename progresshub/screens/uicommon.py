import time
import tkinter as tk
from tkinter import ttk

from .. import theme

_ANIM = {}


def _que(toplevel, ms, fn):
    """Schedule `fn` on the toplevel and track it so it can be cancelled at shutdown."""
    def run():
        _cancel(toplevel, aid)
        try:
            fn()
        except Exception:
            pass
    try:
        aid = toplevel.after(ms, run)
        _ANIM.setdefault(id(toplevel), set()).add(aid)
    except Exception:
        pass


def _cancel(toplevel, aid):
    s = _ANIM.get(id(toplevel))
    if s:
        s.discard(aid)


def cancel_anims(toplevel):
    """Cancel all tracked animation timers for a toplevel (call before destroy)."""
    for aid in _ANIM.pop(id(toplevel), ()):
        try:
            toplevel.after_cancel(aid)
        except Exception:
            pass


def rounded_poly(canvas, x1, y1, x2, y2, r, **kw):
    pts = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kw)


class RoundedFrame(tk.Canvas):
    """Canvas-backed rounded container. Use `.content` to add children."""

    def __init__(self, parent, height=90, radius=16, fill=None, bg=None, pad=16, outline=None, **kw):
        self._fill = fill or theme.FIELD
        self._bg = bg or theme.BG
        self._radius = radius
        px, py = (pad if isinstance(pad, (tuple, list)) else (pad, pad))
        self._padx = kw.pop("padx", px)
        self._pady = kw.pop("pady", py)
        self._outline = outline
        self._h = height
        self._anim = None
        super().__init__(parent, bg=self._bg, height=height, highlightthickness=0, bd=0, **kw)
        self.content = tk.Frame(self, bg=self._fill)
        self._win = self.create_window(0, 0, window=self.content, anchor="nw", tags="content")
        self.bind("<Configure>", self._redraw)

    def _grow_from(self, start, target, ms=240):
        """Animates this frame's height from start up to target (ease-out)."""
        self._h = target
        t0 = time.monotonic()

        def step():
            if not self.winfo_exists():
                return
            now = time.monotonic()
            t = min((now - t0) / ms, 1.0)
            e = 1 - (1 - t) ** 3
            self.config(height=max(int(start + (target - start) * e), 4))
            if t < 1.0:
                self._anim = self.winfo_toplevel()
                _que(self.winfo_toplevel(), 16, step)
            else:
                self._anim = None

        step()

    def _redraw(self, event):
        w, h = event.width, event.height
        self.delete("card")
        if self._outline:
            rounded_poly(self, 0, 0, w, h, self._radius, fill=self._fill,
                         outline=self._outline, width=1, tags="card")
        else:
            rounded_poly(self, 0, 0, w, h, self._radius, fill=self._fill, tags="card")
        self.tag_lower("card")
        self.coords(self._win, self._padx, self._pady)
        self.itemconfigure(self._win, width=max(w - 2 * self._padx, 0),
                           height=max(h - 2 * self._pady, 0))

    def pack(self, **kw):
        kw.setdefault("fill", "x")
        return super().pack(**kw)


def stagger(widget, step=38, rise=175):
    """Gently pops the top-level RoundedFrames inside `widget` into view.

    The grow animation is skipped when the window is fullscreen: each height
    step forces a full recomposite of the (huge) toplevel, which is very slow
    on some Windows/GPU setups. Cards already render at full size natively, so
    this makes fullscreen feel instant.
    """
    try:
        cards = []

        def walk(w, inside=False):
            for c in w.winfo_children():
                if isinstance(c, RoundedFrame):
                    if not inside:
                        cards.append(c)
                    walk(c.content, inside=True)
                else:
                    walk(c, inside)

        walk(widget)
        if not cards:
            return
        root = widget.winfo_toplevel()
        if not root.winfo_exists():
            return
        try:
            if root.attributes("-fullscreen"):
                return
        except tk.TclError:
            pass
        for i, c in enumerate(cards):
            target = c._h
            _que(root, 50 + i * step, lambda c=c, t=target: c._grow_from(6, t, rise))
    except Exception:
        pass


def _blend(hex_a, hex_b, t):
    a, b = theme.hex2rgb(hex_a), theme.hex2rgb(hex_b)
    mix = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
    return "#%02x%02x%02x" % mix


def button(parent, text, command, color=theme.PANEL, width=None):
    if theme.light_mode():
        hover_t = 0.06
        base = _blend(color, theme.TEXT, hover_t)
        hovered = _blend(color, theme.TEXT, hover_t + 0.07)
    else:
        base = color
        hovered = _blend(color, theme.TEXT, 0.12)
    return tk.Button(
        parent, text=text, command=command, bg=base, fg="#11111b",
        activebackground=hovered, activeforeground="#11111b",
        relief="flat", bd=0, cursor="hand2", font=theme.FONT_B, width=width,
    )


def hline(parent):
    return tk.Frame(parent, bg=theme.FIELD, height=1)


def caption(parent, text, bg=None):
    return tk.Label(parent, text=text.upper(), bg=bg or theme.BG, fg=theme.MUTED,
                    font=("Segoe UI", 8, "bold"), anchor="w")


def section(parent, text):
    return tk.Label(parent, text=text.upper(), bg=theme.BG, fg=theme.MUTED,
                    font=theme.FONT_B, anchor="w")


class ScrollFrame(tk.Frame):
    def __init__(self, parent, bg=theme.PANEL):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner.bind("<Configure>", lambda e=None: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e=None: self.canvas.itemconfigure(self.win, width=e.width))
        self._bind_mouse(self.canvas)
        self._bind_mouse(self.inner)

    def _bind_mouse(self, widget):
        widget.bind("<Enter>", lambda e=None: widget.bind_all("<MouseWheel>", self._wheel))
        widget.bind("<Leave>", lambda e=None: widget.unbind_all("<MouseWheel>"))

    def _wheel(self, event):
        self.canvas.yview_scroll(int(-event.delta / 120), "units")


class StatCard:
    def __init__(self, parent, title, value, color=theme.ACCENT, height=84):
        self.x = RoundedFrame(parent, height=height, radius=14, fill=theme.PANEL,
                              pad=14)
        tk.Label(self.x.content, text=title.upper(), bg=theme.PANEL, fg=theme.MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self._value = tk.Label(self.x.content, text=value, bg=theme.PANEL, fg=color,
                               font=("Segoe UI", 19, "bold"), anchor="w")
        self._value.pack(anchor="w", pady=(2, 0))
        self.frame = self.x

    def set_value(self, text, color=None):
        self._value.config(text=text)
        if color:
            self._value.config(fg=color)

    def pack(self, **kw):
        self.x.pack(**kw)


def stat_card(parent, title, value, color=theme.ACCENT, height=84):
    return StatCard(parent, title, value, color, height)


class PlaceholderEntry(tk.Entry):
    def __init__(self, parent, placeholder, show=None, **kw):
        self.placeholder = placeholder
        self.ph_active = True
        self.show_char = show or ""
        kw.setdefault("bg", theme.FIELD)
        kw.setdefault("show", "")
        kw.setdefault("fg", theme.MUTED)
        kw.setdefault("insertbackground", theme.TEXT)
        kw.setdefault("relief", "flat")
        kw.setdefault("bd", 0)
        kw.setdefault("font", theme.FONT)
        super().__init__(parent, **kw)
        self.insert(0, placeholder)
        self.bind("<FocusIn>", self._focus_in)
        self.bind("<FocusOut>", self._focus_out)

    def _focus_in(self, _e):
        if self.ph_active:
            self.delete(0, "end")
            self.config(fg=theme.TEXT, show=self.show_char)
            self.ph_active = False

    def _focus_out(self, _e):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=theme.MUTED, show="")
            self.ph_active = True

    def get_value(self):
        if self.ph_active:
            return ""
        return self.get()


def modal(parent, title, text):
    win = tk.Toplevel(parent)
    win.title(title)
    win.configure(bg=theme.PANEL)
    win.resizable(False, False)
    tk.Label(win, text=text, bg=theme.PANEL, fg=theme.TEXT, font=theme.FONT,
             wraplength=380, justify="center").pack(pady=20, padx=20)
    btn = button(win, "Okay", win.destroy, theme.ACCENT)
    btn.pack(pady=10, ipadx=24)
    _center(win, parent)


def _center(win, parent):
    win.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width() - win.winfo_width()) // 2
    y = parent.winfo_rooty() + (parent.winfo_height() - win.winfo_height()) // 2
    win.geometry(f"+{max(x, 0)}+{max(y, 0)}")
    win.grab_set()


def tree(parent, columns, **kw):
    style = ttk.Style(parent)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure(
        "PH.Treeview",
        background=theme.FIELD,
        fieldbackground=theme.FIELD,
        foreground=theme.TEXT,
        borderwidth=0,
        relief="flat",
        rowheight=26,
        font=theme.FONT_S,
    )
    style.configure(
        "PH.Treeview.Heading",
        background=theme.PANEL,
        foreground=theme.MUTED,
        borderwidth=0,
        relief="flat",
        font=theme.FONT_B,
    )
    style.map("PH.Treeview", background=[("selected", theme.ACCENT)],
              foreground=[("selected", "#11111b")])
    t = ttk.Treeview(parent, columns=columns, show="headings", style="PH.Treeview", **kw)
    for c in columns:
        t.heading(c, text=c.upper())
        t.column(c, anchor="center", width=90)
    return t