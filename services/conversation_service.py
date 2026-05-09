import json
import uuid
from datetime import datetime
from pathlib import Path

_CONVS_DIR = Path.home() / ".issbc" / "convs"


def _ensure_dir():
    _CONVS_DIR.mkdir(parents=True, exist_ok=True)


def new_conv_id() -> str:
    return f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"


def save_conv(conv_id: str, data: dict) -> None:
    _ensure_dir()
    data["updated_at"] = datetime.now().isoformat(timespec="seconds")
    (_CONVS_DIR / f"{conv_id}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_convs() -> list:
    _ensure_dir()
    convs = []
    for f in _CONVS_DIR.glob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            convs.append({
                "id": d.get("id", f.stem),
                "name": d.get("name", "Sin título"),
                "updated_at": d.get("updated_at", ""),
            })
        except Exception:
            pass
    return sorted(convs, key=lambda x: x["updated_at"], reverse=True)


def load_conv(conv_id: str) -> dict:
    p = _CONVS_DIR / f"{conv_id}.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def delete_conv(conv_id: str) -> None:
    p = _CONVS_DIR / f"{conv_id}.json"
    if p.exists():
        p.unlink()
