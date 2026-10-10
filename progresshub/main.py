import sys
import traceback

import tkinter as tk

from .screens.auth import AuthScreen
from .screens.uicommon import cancel_anims, stagger
from .screens.uicommon import _que
from . import db, settings as appsettings, theme


class App:
    def __init__(self, root, settings=None):
        self.root = root
        self.user = None
        self.current = None
        self._settings = settings or appsettings.load()
        self._screen_cls = None
        self._screen_kw = {}
        db.init_db()
        appsettings.apply(self._settings)
        root.title("ProgressHub")
        root.configure(bg=theme.BG)
        root.protocol("WM_DELETE_WINDOW", self.quit)
        root.bind_all("<F11>", lambda e=None: self.toggle_fullscreen())
        if self._settings.get("fullscreen", True):
            self.set_fullscreen(True)
        self.show_screen(AuthScreen)

    def set_user(self, user):
        self.user = user

    def show_screen(self, screen_cls, **kw):
        if self.current is not None:
            self.current.destroy()
        self._screen_cls = screen_cls
        self._screen_kw = kw
        self.current = screen_cls(self, **kw)
        self.current.pack(fill="both", expand=True)
        _que(self.root, 10, lambda: stagger(self.current))

    def set_theme(self, mode, fullscreen=None):
        self._settings["theme"] = mode
        if fullscreen is not None:
            self._settings["fullscreen"] = fullscreen
            self.set_fullscreen(fullscreen)
        appsettings.save(self._settings)
        appsettings.apply(self._settings)
        self.rebuild_current()

    def rebuild_current(self):
        if self._screen_cls is not None:
            self.show_screen(self._screen_cls, **self._screen_kw)

    def set_fullscreen(self, on):
        try:
            self.root.attributes("-fullscreen", bool(on))
        except tk.TclError:
            pass

    def toggle_fullscreen(self):
        w = self.root.focus_displayof()
        if w is not None:
            top = w.winfo_toplevel()
            if top is not self.root:
                cur = top.attributes("-fullscreen")
                try:
                    top.attributes("-fullscreen", not cur)
                except tk.TclError:
                    pass
                return
        cur = self.root.attributes("-fullscreen")
        self.set_fullscreen(not cur)
        self._settings["fullscreen"] = not cur
        appsettings.save(self._settings)

    def quit(self):
        cancel_anims(self.root)
        self.root.destroy()


def main():
    try:
        from progresshub import APP_NAME
        st = appsettings.load()
        root = tk.Tk()
        root.title(APP_NAME)
        App(root, st)
        root.mainloop()
    except Exception:
        traceback.print_exc()
        input("Press Enter to close...")
        sys.exit(1)


if __name__ == "__main__":
    main()