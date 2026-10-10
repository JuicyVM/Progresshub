FONT = ("Segoe UI", 10)
FONT_B = ("Segoe UI", 10, "bold")
FONT_T = ("Segoe UI", 16, "bold")
FONT_XL = ("Segoe UI", 22, "bold")
FONT_L = ("Segoe UI", 13, "bold")
FONT_S = ("Segoe UI", 9)
FONT_MONO = ("Cascadia Mono", 10)

# Ordered: name -> (bg, panel, field, text, muted, accent, green, orange, status, purple, cyan)
# Surfaces that must adapt when a light palette is active get extra light-skins.
_THEMES = {
    "midnight": {
        "label": "Midnight (dark)",
        "bg": "#1e1e2e", "panel": "#2a2a3c", "field": "#313244",
        "text": "#cdd6f4", "muted": "#6c7086", "accent": "#7aa2f7",
        "green": "#9ece6a", "orange": "#f7768e", "status": "#e0af68",
        "purple": "#cba6f7", "cyan": "#89dceb", "line": "#3a3b50",
        "light": False,
    },
    "ember": {
        "label": "Ember (warm dark)",
        "bg": "#16140f", "panel": "#211e18", "field": "#2b2620",
        "text": "#efe3c9", "muted": "#8a7f6d", "accent": "#ff9f68",
        "green": "#a3be8c", "orange": "#ff6b6b", "status": "#ffd166",
        "purple": "#d6b3f0", "cyan": "#9ad7dc", "line": "#2f2a22",
        "light": False,
    },
    "abyss": {
        "label": "Abyss (near black)",
        "bg": "#0d0f14", "panel": "#13161d", "field": "#1a1e27",
        "text": "#d7dce8", "muted": "#5a6474", "accent": "#5aa0ff",
        "green": "#62de8c", "orange": "#ff5c72", "status": "#f5c86a",
        "purple": "#b98bff", "cyan": "#5fd8e8", "line": "#20242f",
        "light": False,
    },
    "daylight": {
        "label": "Daylight (light)",
        "bg": "#eef0f5", "panel": "#ffffff", "field": "#e6e8ef",
        "text": "#1c1e28", "muted": "#6f7286", "accent": "#4b63e6",
        "green": "#2c9d4f", "orange": "#e3546e", "status": "#b8791f",
        "purple": "#8b5cf6", "cyan": "#0e9bb0", "line": "#dcdfe8",
        "light": True,
    },
}

# module-level globals mirror the active theme (referenced as theme.BG etc.)
BG = PANEL = FIELD = TEXT = MUTED = ACCENT = GREEN = ORANGE = STATUS = PURPLE = CYAN = LINE = None
_active_mode = None
_CUSTOM_ACCENT = None


def set_accent(hexc):
    """Overrides the accent color (custom color wheel). Persisted by callers."""
    global ACCENT, _CUSTOM_ACCENT
    _CUSTOM_ACCENT = hexc
    ACCENT = hexc


def reset_accent():
    global _CUSTOM_ACCENT
    _CUSTOM_ACCENT = None


def has_custom_accent():
    return _CUSTOM_ACCENT is not None


def current_accent():
    return _CUSTOM_ACCENT if _CUSTOM_ACCENT else (_THEMES.get(_active_mode) or _THEMES["midnight"])["accent"]


def _detect_windows_dark():
    try:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        ) as k:
            value, _ = winreg.QueryValueEx(k, "AppsUseLightTheme")
            return value == 0
    except Exception:
        return True


def set_theme(mode):
    """mode: theme key, or 'system' to follow the OS. Re-assigns module globals."""
    global BG, PANEL, FIELD, TEXT, MUTED, ACCENT, GREEN, ORANGE, STATUS, PURPLE, CYAN, LINE, _active_mode
    if mode == "system":
        mode = "midnight" if _detect_windows_dark() else "daylight"
    data = _THEMES.get(mode, _THEMES["midnight"])
    BG, PANEL, FIELD = data["bg"], data["panel"], data["field"]
    TEXT, MUTED = data["text"], data["muted"]
    ACCENT, GREEN, ORANGE, STATUS = data["accent"], data["green"], data["orange"], data["status"]
    PURPLE, CYAN, LINE = data["purple"], data["cyan"], data["line"]
    _active_mode = mode
    if _CUSTOM_ACCENT:
        ACCENT = _CUSTOM_ACCENT
    return data


def active_mode():
    return _active_mode


def light_mode():
    return _themes_get(_active_mode).get("light", False)


def _themes_get(mode):
    return _THEMES.get(mode, _THEMES["midnight"])


def theme_choices():
    return [(k, v["label"]) for k, v in _THEMES.items()]


# make sure globals are set before first use
set_theme("midnight")


def hex2rgb(hex_str):
    h = hex_str.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))