import json
from pathlib import Path

_SETTINGS_FILE = Path.home() / ".issbc" / "settings.json"

_DEFAULTS = {
    "ollama_model": "qwen2.5:7b",
    "font_size": 13,
    "extra_prompt": "",
}


def load_settings() -> dict:
    if _SETTINGS_FILE.exists():
        try:
            data = json.loads(_SETTINGS_FILE.read_text(encoding="utf-8"))
            return {**_DEFAULTS, **data}
        except Exception:
            pass
    return dict(_DEFAULTS)


def save_settings(settings: dict) -> None:
    _SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _SETTINGS_FILE.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8"
    )
