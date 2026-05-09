import json
from pathlib import Path

_DATA_DIR = Path.home() / ".issbc"
_SESSION_FILE = _DATA_DIR / "session.json"


def _ensure_dir():
    _DATA_DIR.mkdir(exist_ok=True)


def save_session(model) -> None:
    _ensure_dir()
    # Only persist PDF paths that still exist on disk
    pdfs_to_save = [
        {"path": p["path"], "name": p["name"]}
        for p in model.pdfs
        if Path(p["path"]).exists()
    ]
    data = {
        "history": model.history[:50],
        "pdfs": pdfs_to_save,
        "last_symptoms": model.symptoms,
        "chat_history": model.chat_history[-40:],  # keep last 40 messages
    }
    _SESSION_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_session() -> dict:
    if not _SESSION_FILE.exists():
        return {}
    try:
        return json.loads(_SESSION_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}
