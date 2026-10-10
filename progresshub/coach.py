import statistics as stats

from . import db


def _money(v, sym="$"):
    sign = "-" if v < 0 else ""
    return f"{sign}{sym}{abs(v):,.2f}"


def report(project):
    ptype = project["ptype"]
    if ptype == "gym":
        return _gym_report(project)
    if ptype == "trading":
        return _trading_report(project)
    if ptype in ("weight_loss", "calorie"):
        return _health_report(project)
    if ptype in ("sleep", "savings", "study", "cardio", "reading", "habits"):
        return _simple_report(project)
    return "Unknown project type."


SIMPLE_META = {
    "sleep": ("sleep_log", "hours", "Sleep"),
    "savings": ("savings_log", "amount", "Savings"),
    "study": ("study_log", "hours", "Study"),
    "cardio": ("cardio_log", "distance", "Cardio"),
    "reading": ("reading_log", "pages", "Reading"),
    "habits": ("habit_log", None, "Habits"),
}


def _simple_report(project):
    table, col, label = SIMPLE_META[project["ptype"]]
    pid = project["id"]
    rows = db.simple_rows(table, pid, limit=100000)
    lines = [f"{label.upper()} COACH REPORT", "=" * 34]
    if not rows:
        lines.append("No data yet.")
        lines += [""] if False else []
        lines.append("Log your first entry and I'll give you the trend.")
        return "\n".join(lines)
    if project["ptype"] == "habits":
        done = sum(1 for r in rows if r["done"])
        habits = len({r["habit"] for r in rows})
        lines.append(f"Check-ins: {done}   habits tracked: {habits}")
        lines.append(f"Current streak: {db.habit_streak(pid)} days")
        series = db.habit_series(pid)
        if len(series) >= 7:
            avg7 = sum(v for _, v in series[-7:]) / 7
            lines.append(f"Avg habits/day (last 7): {avg7:.1f}")
        lines.append("")
        lines.append("Tip: 2-minute rule - make the habit laughably small to start.")
        return "\n".join(lines)
    total = sum(r[col] for r in rows)
    if table == "sleep_log":
        avg = total / len(rows)
        best = max(r[col] for r in rows)
        lines.append(f"Entries: {len(rows)}   span {rows[-1]['ts']} - {rows[0]['ts']}")
        lines.append(f"Avg sleep: {avg:.1f} h/night   best: {best:g} h")
        if avg < 7:
            lines.append("You're under 7h average - recovery is where gains happen.")
        else:
            lines.append("Solid sleep average. That's the foundation right there.")
    elif table == "savings_log":
        sym = db.currency_symbol(project)
        deposits = len(rows)
        biggest = max(r[col] for r in rows)
        series = db.simple_series(table, pid, col)
        lines.append(f"Total saved: {sym}{total:,.0f}  ({deposits} deposits, biggest {sym}{biggest:,.0f})")
        if len(series) >= 4:
            first4 = sum(v for _, v in series[:4])
            last4 = sum(v for _, v in series[-4:])
            lines.append("Momentum: " + ("accelerating" if last4 >= first4 else "cooling off - keep the habit"))
    elif table == "study_log":
        subs = {}
        for r in rows:
            subs[r["subject"]] = subs.get(r["subject"], 0) + r[col]
        top = sorted(subs.items(), key=lambda kv: -kv[1])[0]
        lines.append(f"Total: {total:,.1f} h across {len(subs)} subjects ({len(rows)} sessions)")
        lines.append(f"Top subject: {top[0]} ({top[1]:.1f} h)")
    elif table == "cardio_log":
        best = max(r[col] for r in rows)
        mins = sum(r["minutes"] for r in rows if r.get("minutes"))
        lines.append(f"Total: {total:,.1f} km across {len(rows)} workouts")
        lines.append(f"Longest: {best:g} km   total time: {mins} min")
    elif table == "reading_log":
        books = len({r["book"] for r in rows})
        lines.append(f"Total: {total:,.0f} pages ({books} books, {len(rows)} sessions)")
        avg = total / len(rows)
        lines.append(f"Avg {avg:,.0f} pages/session")
    else:
        lines.append(f"Total: {total:,.1f}")
    lines.append("")
    lines.append(f"Tip for {label.lower()}: consistency beats intensity - show up daily.")
    return "\n".join(lines)


def _gym_report(project):
    pid = project["id"]
    sets = db.gym_sets(pid, limit=100000)
    if not sets:
        return (
            "No gym data yet.\n\n"
            "Log your first set (exercise, weight, reps) and I'll break down volume, "
            "PRs, and consistency for you."
        )
    total_volume = sum(s["weight"] * s["reps"] for s in sets)
    days = {s["ts"] for s in sets}
    recent = sum(1 for d in days if d[:7] == db.today()[:7])
    lines = ["GYM COACH REPORT", "=" * 34]
    lines.append(f"Logs: {len(sets)} sets across {len(days)} workout days")
    lines.append(f"Total volume lifted: {total_volume:,.0f} kg")
    if recent:
        lines.append(f"Workouts this month: {recent}")
    lines.append("")
    lines.append("LIFTING PRs (best weight logged):")
    for e in db.gym_exercises(pid)[:8]:
        from .calc import one_rep_max
        est = one_rep_max(e["max_weight"], 1)
        lines.append(f"  {e['exercise']:<14} {e['max_weight']:>7.1f} kg  (est 1RM {est:,.0f})")
    if len(days) >= 2:
        vol = db.gym_weekly_volume(pid)
        lens = len(vol)
        avg1 = vol[lens // 2][1] / max(lens - lens // 2, 1)
        avg0 = vol[:lens // 2][0][1] if vol[:lens // 2] else 0
        trend = "up" if avg0 > 0 and vol[-1][1] > avg0 else "down or flat"
        lines.append("")
        lines.append(f"Monthly volume trend: {trend}")
    lines.append("")
    lines.append("Tip: progressive overload > going to failure every set.")
    return "\n".join(lines)


def _trading_report(project):
    pid = project["id"]
    sym = db.currency_symbol(project)
    rows = db.trades(pid, limit=100000)
    if not rows:
        return (
            "No trades logged yet.\n\n"
            "Add your trades (entry, exit, size) and I'll compute P/L, win rate, "
            "profit factor, and your equity curve."
        )
    pnls = [t["pnl"] for t in rows]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    total = sum(pnls)
    win_rate = len(wins) / len(pnls) * 100
    avg_w = stats.mean(wins) if wins else 0
    avg_l = stats.mean(losses) if losses else 0
    profit_factor = (sum(wins) / abs(sum(losses))) if losses else float("inf")

    lines = ["TRADING COACH REPORT", "=" * 34]
    lines.append(f"Trades: {len(rows)}   Symbols: {len({t['symbol'] for t in rows})}")
    lines.append(f"Net P/L: {_money(total, sym)}")
    lines.append(f"Win rate: {win_rate:.1f}%")
    if wins:
        lines.append(f"Avg win: {_money(avg_w, sym)}   Avg loss: {_money(avg_l, sym)}")
    lines.append(f"Profit factor: {profit_factor if profit_factor != float('inf') else 'inf'}")
    if len(pnls) >= 5:
        recent = sum(pnls[-5:])
        lines.append(f"Last 5 trades: {_money(recent, sym)}")
    lines.append("")
    if wins and losses:
        wr = win_rate / 100
        r_mul = avg_w / abs(avg_l)
        break_even_r = (1 - wr) / max(wr, 1e-9)
        lines.append(
            f"Edge check: avg win = {r_mul:.2f}R vs "
            f"break-even {break_even_r:.2f}R at your win rate"
        )
        lines.append("")
    lines.append("Tip: cut losers fast, let winners run. Consistency beats hero shots.")
    return "\n".join(lines)


def _health_report(project):
    pid = project["id"]
    if project["ptype"] == "calorie":
        by_day = db.daily_calories(pid)
        if not by_day:
            return "No meals logged yet. Track a meal and I'll show your daily calorie trend."
        avg_cal = stats.mean(c for _, c in by_day)
        lines = ["CALORIE COUNTER REPORT", "=" * 34]
        lines.append(f"Days tracked: {len(by_day)}")
        lines.append(f"Avg daily intake: {avg_cal:,.0f} kcal")
        last = by_day[-1][1]
        lines.append(f"Today: {last:,.0f} kcal")
        goal = 2500
        lines.append(f"Against a {goal:,} kcal goal: {'balanced' if avg_cal * 0.9 <= goal <= avg_cal * 1.1 else 'over' if avg_cal > goal else 'under'}")
        lines.append("")
        lines.append("Tip: protein > 1.6 g/kg keeps muscle while cutting.")
        return "\n".join(lines)

    bws = db.body_weight(pid)
    if not bws:
        return (
            "No weight entries yet.\n\n"
            "Log your weight a few times a week. Trend beats daily noise."
        )
    first, last = bws[0]["weight"], bws[-1]["weight"]
    change = last - first
    days = len(bws)
    lines = ["WEIGHT LOSS REPORT", "=" * 34]
    lines.append(f"Entries: {days}   Span: {bws[0]['ts']} to {bws[-1]['ts']}")
    lines.append(f"{first:.1f} kg  ->  {last:.1f} kg")
    lines.append(f"Total change: {change:+.1f} kg")
    if days >= 3:
        weekly = change / max(days / 7, 1)
        lines.append(f"Avg weekly rate: {weekly:+.2f} kg/week  (healthy: -0.5 to -1.0)")
    lines.append("")
    lines.append("Tip: fat loss is calories in vs out. Weigh in at the same time daily.")
    return "\n".join(lines)


def answer(project, question):
    q = (question or "").lower()
    if not q:
        return "Ask me anything about your progress - I analyze your actual data."
    if any(w in q for w in ("trade", "win rate", "pnl", "profit", "stock", "p&l")):
        if project["ptype"] != "trading":
            return "This question is more for a Trading project. Create one and I'll be all over it."
        return _trading_report(project)
    if any(w in q for w in ("gym", "lift", "bench", "squat", "deadlift", "workout", "pr", "reps")):
        if project["ptype"] != "gym":
            return "That's gym talk! Open a Gym project and I'll break down your lifts."
        return _gym_report(project)
    if any(w in q for w in ("weight", "calorie", "fat", "diet", "meal", "body")):
        return _health_report(project)
    if any(w in q for w in ("sleep", "savings", "study", "read", "cardio", "run", "habit")):
        return _simple_report(project)
    return (
        "I'm your local coach. Try questions like:\n"
        "  - 'how's my trading going?'\n"
        "  - 'gym report'\n"
        "  - 'show me my weight trend'\n"
        "I read your actual logged data - no cloud, everything stays on your PC."
    )


def chat_system(project):
    """System prompt sent to the LLM when a key is configured."""
    title = db.PROJECT_TYPES.get(project["ptype"], project["ptype"])
    return (
        "You are Coach, a sharp but friendly personal performance coach inside "
        "ProgressHub, a desktop goal-tracking app. The user tracks real numbers and "
        "wants honest, practical advice.\n"
        f"Project: \"{project['name']}\" ({title}).\n\n"
        "Here is a computed snapshot of their actual logged data - use it as ground "
        "truth and refer to it, but stay conversational:\n"
        + report(project) + "\n\n"
        "Be concise (under ~120 words unless asked), motivating, and specific to their "
        "numbers. No fluff, no generic gym-bro lines."
    )


def llm_reply(key, base_url, model, messages, timeout=60):
    """Calls an OpenAI-compatible chat-completions endpoint. Returns assistant text."""
    import json
    import urllib.request

    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.6,
        "max_tokens": 600,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.load(resp)
    return data["choices"][0]["message"]["content"].strip()