import math

from . import theme


def draw_line_chart(canvas, points, width, height, color=theme.ACCENT):
    """points: list of (label, value). Draws a simple line chart on a tk Canvas."""
    canvas.delete("all")
    pad_l, pad_r, pad_t, pad_b = 46, 14, 14, 26
    iw, ih = width - pad_l - pad_r, height - pad_t - pad_b
    if iw <= 0 or ih <= 0:
        return

    canvas.create_rectangle(0, 0, width, height, fill=theme.PANEL, outline=theme.PANEL)

    if not points:
        canvas.create_text(
            width / 2, height / 2, text="No data yet - add some!", fill=theme.MUTED,
            font=theme.FONT,
        )
        return

    max_pts = 128
    if len(points) > max_pts:
        step = (len(points) - 1) / (max_pts - 1)
        idx = [int(round(i * step)) for i in range(max_pts)]
        idx = sorted(set(idx))
        points = [points[i] for i in idx]

    values = [v for _, v in points]
    lo, hi = min(values), max(values)
    if hi == lo:
        hi, lo = hi + 1, lo - 1
    spread = hi - lo

    def px(i):
        return pad_l + (i * iw / max(len(points) - 1, 1))

    def py(v):
        return pad_t + ih - ((v - lo) / spread) * ih

    for g in range(3):
        gy = pad_t + ih * (g / 2)
        canvas.create_line(pad_l, gy, pad_l + iw, gy, fill=theme.FIELD)
        val = lo + spread * (1 - g / 2)
        canvas.create_text(
            pad_l - 6, gy, text=f"{val:,.1f}", fill=theme.MUTED, font=theme.FONT_S,
            anchor="e",
        )

    coords = [px(i) for i in range(len(points))]
    ys = [py(v) for v in values]
    if len(points) >= 2:
        canvas.create_line(*[c for pair in zip(coords, ys) for c in pair],
                           fill=color, width=2)
    for x, y in zip(coords, ys):
        canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=color, outline="")

    labels = [p[0] for p in points]
    if len(labels) > 1:
        step = max(len(labels) // 6, 1)
        for i in range(0, len(labels), step):
            canvas.create_text(
                px(i), height - 10, text=labels[i], fill=theme.MUTED, font=theme.FONT_S,
            )


def round_nice(v):
    if v is None:
        return 0
    if abs(v) >= 100:
        return round(v)
    return round(v, 1)