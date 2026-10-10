import threading
import tkinter as tk
from tkinter import ttk

from .uicommon import button
from .. import coach, db, settings as appsettings, theme


class CoachWindow(tk.Toplevel):
    def __init__(self, parent, project=None):
        super().__init__(parent)
        self.app = parent.app
        self.title("Coach AI")
        self.configure(bg=theme.PANEL)
        self.geometry("640x560")
        self.minsize(520, 420)
        self.resizable(True, True)
        self.transient(parent)
        self.context = project
        self.history = []

        projects = db.list_projects(self.app.user["id"])
        self.by_name = {}
        names = []
        if self.context:
            names.append(self.context["name"])
            self.by_name[self.context["name"]] = self.context
        for p in projects:
            if p["name"] not in self.by_name:
                names.append(p["name"])
                self.by_name[p["name"]] = p
        if not names:
            names = [""]

        top = tk.Frame(self, bg=theme.PANEL, padx=16)
        top.pack(fill="x", pady=(14, 6))
        tk.Label(top, text="COACH AI", bg=theme.PANEL, fg=theme.PURPLE,
                 font=("Segoe UI", 15, "bold")).pack(side="left")
        self.cb = ttk.Combobox(top, values=names, state="readonly", font=theme.FONT)
        self.cb.set(names[0] or "")
        self.cb.pack(side="right")

        btn_row = tk.Frame(self, bg=theme.PANEL, padx=16)
        btn_row.pack(fill="x")
        button(btn_row, "Analyze for me", self._analyze, theme.PURPLE).pack(
            side="left", ipadx=10)
        button(btn_row, "Clear chat", self._clear, theme.PANEL).pack(side="right", ipadx=10)

        chat_bg = theme.PANEL if theme.light_mode() else theme.BG
        self.log = tk.Text(self, bg=chat_bg, fg=theme.TEXT, font=theme.FONT, wrap="word",
                           relief="flat", bd=0, padx=16, pady=12, state="disabled")
        self.log.pack(fill="both", expand=True, padx=16, pady=(8, 4))
        self.log.tag_configure("you", foreground=theme.ACCENT, font=theme.FONT_B)
        self.log.tag_configure("coach", foreground=theme.TEXT)
        self.log.tag_configure("sys", foreground=theme.MUTED, font=theme.FONT_S)
        self.log.tag_configure("err", foreground=theme.ORANGE, font=theme.FONT_B)

        qrow = tk.Frame(self, bg=theme.PANEL, padx=16)
        qrow.pack(fill="x", pady=(0, 14))
        self.q = tk.Entry(qrow, bg=theme.FIELD, fg=theme.TEXT, insertbackground=theme.TEXT,
                          relief="flat", font=theme.FONT)
        self.q.pack(side="left", fill="x", expand=True, ipady=8)
        self.q.bind("<Return>", lambda e=None: self._ask())
        button(qrow, "Send", self._ask, theme.PURPLE).pack(side="left", padx=(8, 0),
                                                           ipadx=14, ipady=6)

        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        self.grab_set()

        self._say("Hey! I'm your Coach AI. Select a project and hit 'Analyze for me', "
                  "or just talk to me - I read your real logged data.", "sys")
        if not self._key():
            self._say("Tip: add an OpenAI-style API key in Settings \u2192 AI Coach and I'll "
                      "answer like a real human coach.", "sys")
        self._analyze()

    # ------------------------------------------------------------- helpers

    def _pick(self):
        return self.by_name.get(self.cb.get())

    def _key(self):
        st = appsettings.load()
        return st.get("ai_key", "").strip()

    def _params(self):
        st = appsettings.load()
        return st.get("ai_base", "https://api.openai.com/v1"), st.get("ai_model", "gpt-4o-mini")

    def _say(self, text, tag="coach"):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n\n")
        self.log.configure(state="disabled")
        self.log.see("end")

    def _bubble(self, role, text):
        self.history.append((role, text))
        self.history = self.history[-12:]
        self.log.configure(state="normal")
        self.log.insert("end", ("YOU" if role == "user" else "COACH") + "\n", "you" if role == "user" else "coach")
        self.log.insert("end", text + "\n\n", "you" if role == "user" else "coach")
        self.log.configure(state="disabled")
        self.log.see("end")

    # ------------------------------------------------------------- actions

    def _analyze(self):
        p = self._pick()
        if not p:
            self._say("Create a project first, then I can analyze it.", "err")
            return
        self._ask_free("Analyze my whole project and give me a full breakdown.")

    def _ask(self):
        q = self.q.get().strip()
        if not q:
            return
        self.q.delete(0, "end")
        self._ask_free(q)

    def _ask_free(self, q):
        p = self._pick()
        if not p:
            self._bubble("user", q)
            self._say("No project selected - pick one in the top-right corner.", "err")
            return
        self._bubble("user", q)
        if not self._key():
            self._local_reply(p, q)
            return
        self._thinking()
        threading.Thread(target=self._llm_worker, args=(p, q), daemon=True).start()

    def _local_reply(self, p, q):
        text = coach.answer(p, q)
        if not self._key():
            text += ("\n\n(psst - add an API key in Settings \u2192 AI Coach and I'll "
                     "answer like a real human coach.)")
        self._bubble("assistant", text)

    def _thinking(self):
        self.log.configure(state="normal")
        self._think_mark = self.log.index("end-1c")
        self.log.insert("end", "COACH is thinking...\n\n", "sys")
        self.log.configure(state="disabled")
        self.log.see("end")

    def _unthink(self):
        self.log.configure(state="normal")
        if getattr(self, "_think_mark", None):
            try:
                self.log.delete(self._think_mark, "end-1c")
            except tk.TclError:
                pass
        self.log.configure(state="disabled")

    def _llm_worker(self, p, q):
        try:
            base, model = self._params()
            msgs = [{"role": "system", "content": coach.chat_system(p)}]
            for role, text in self.history[:-1]:
                msgs.append({"role": "user" if role == "user" else "assistant", "content": text})
            msgs.append({"role": "user", "content": q})
            text = coach.llm_reply(self._key(), base, model, msgs)
            self.after(0, lambda: (self._unthink(), self._bubble("assistant", text)))
        except Exception as exc:
            self.after(0, lambda: (
                self._unthink(),
                self._bubble("assistant", f"Couldn't reach the AI: {exc}\n\n"
                                          "Check your API key in Settings, or I'll fall back "
                                          "to my local brain."),
            ))

    def _clear(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self.history = []
        self._say("Chat cleared. Ask me anything about your progress.", "sys")