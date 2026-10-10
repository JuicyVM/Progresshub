import json
from pathlib import Path

from . import i18n, theme

SETTINGS_PATH = Path(__file__).parent / "settings.json"

DEFAULTS = {
    "theme": "system",
    "fullscreen": True,
    "ai_key": "",
    "ai_base": "https://api.openai.com/v1",
    "ai_model": "gpt-4o-mini",
    "lang": "en",
    "accent": None,
}


def load():
    data = dict(DEFAULTS)
    try:
        if SETTINGS_PATH.exists():
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data.update(json.load(f))
    except Exception:
        pass
    return data


def save(settings):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def apply(settings):
    """Applies a settings dict to the app (theme globals, language, accent)."""
    i18n.set_lang(settings.get("lang") or "en")
    theme.set_theme(settings.get("theme", "system"))
    acc = settings.get("accent")
    if acc:
        theme.set_accent(acc)
    elif theme.has_custom_accent():
        theme.reset_accent()
    return None
