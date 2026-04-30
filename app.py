import json
import os
import uuid
import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, abort, send_from_directory

app = Flask(__name__)

CONFIG_PATH   = os.path.join(os.path.dirname(__file__), "config.json")
MESSAGES_PATH = os.path.join(os.path.dirname(__file__), "messages.json")
DOCS_PATH     = os.path.join(os.path.dirname(__file__), "docs")
MANUALS_PATH  = os.path.join(os.path.dirname(__file__), "manuals")
MANUALS_INDEX_PATH = os.path.join(MANUALS_PATH, "assets_manuals_index.json")

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


# ── Config ─────────────────────────────────────────────────────────────────────

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def load_manual_index() -> list:
    if not os.path.exists(MANUALS_INDEX_PATH):
        abort(503, "Manual index not yet built. Run scripts/build_manuals_index.py first.")
    with open(MANUALS_INDEX_PATH, "r") as f:
        return json.load(f)


def find_manual_asset(asset_tag: str) -> dict | None:
    needle = asset_tag.strip().lower()
    if not needle:
        return None
    for asset in load_manual_index():
        if asset.get("asset_tag", "").lower() == needle:
            return asset
    return None


# ── Messages persistence ────────────────────────────────────────────────────────

def load_messages() -> list:
    if not os.path.exists(MESSAGES_PATH):
        return []
    with open(MESSAGES_PATH, "r") as f:
        return json.load(f)


def save_messages(messages: list) -> None:
    with open(MESSAGES_PATH, "w") as f:
        json.dump(messages, f, indent=2)


def active_messages(messages: list) -> list:
    """Return all currently active messages sorted high → low priority."""
    now = datetime.datetime.now().isoformat()
    active = [
        m for m in messages
        if m.get("start", "") <= now <= m.get("end", "")
    ]
    return sorted(active, key=lambda m: PRIORITY_ORDER.get(m.get("priority", "low"), 2))


# ── Routes ──────────────────────────────────────────────────────────────────────

@app.get("/")
def index():
    config   = load_config()
    messages = load_messages()
    banners  = active_messages(messages)
    return render_template("index.html", sections=config["sections"], banners=banners)


_DOC_SECTIONS = [
    ("System Design",     "SystemDesign"),
    ("System Operations", "SystemOperations"),
    ("Other",             None),
]


@app.get("/docs/")
def docs_index():
    if not os.path.isdir(DOCS_PATH):
        abort(503, "Documentation not yet published. Run publish_docs.sh first.")
    html_files = sorted(
        f for f in os.listdir(DOCS_PATH)
        if f.endswith(".html") and not f.startswith("_")
    )
    # Group by prefix; strip prefix from display name
    sections = []
    claimed = set()
    for title, prefix in _DOC_SECTIONS:
        if prefix:
            matched = [f for f in html_files if f.startswith(prefix)]
            claimed.update(matched)
        else:
            matched = [f for f in html_files if f not in claimed]
        docs = [
            {
                "name": f.replace(".html", "")[len(prefix):] if prefix else f.replace(".html", ""),
                "file": f,
            }
            for f in matched
        ]
        if docs:
            sections.append({"title": title, "docs": docs})
    return render_template("docs_index.html", sections=sections)


@app.get("/docs/<path:filename>")
def serve_docs(filename):
    if not os.path.isdir(DOCS_PATH):
        abort(503, "Documentation not yet published. Run publish_docs.sh first.")
    return send_from_directory(DOCS_PATH, filename)


@app.get("/manuals/")
def manuals_index():
    if not os.path.isdir(MANUALS_PATH):
        abort(503, "Manuals not yet published. Run publish_manuals.sh first.")
    return render_template("manuals_index.html", assets=load_manual_index())


@app.get("/manuals/files/<path:filename>")
def serve_manual(filename):
    if not os.path.isdir(MANUALS_PATH):
        abort(503, "Manuals not yet published. Run publish_manuals.sh first.")
    requested = Path(filename)
    if requested.name.startswith(".") or requested.suffix.lower() != ".pdf":
        abort(404)
    return send_from_directory(MANUALS_PATH, filename)


@app.get("/api/manuals/<asset_tag>")
def api_manuals_for_asset(asset_tag):
    asset = find_manual_asset(asset_tag)
    if asset is None:
        abort(404, f"no manuals found for asset tag {asset_tag}")
    return jsonify(
        {
            "asset_tag": asset["asset_tag"],
            "manual_count": asset["manual_count"],
            "manuals": asset["manuals"],
        }
    )


@app.get("/admin/messages")
def messages_admin():
    return render_template("messages.html")


# ── Messages API ────────────────────────────────────────────────────────────────

@app.get("/api/messages")
def api_list_messages():
    return jsonify(load_messages())


@app.post("/api/messages")
def api_create_message():
    data = request.get_json(force=True)
    messages = load_messages()
    msg = {
        "id":       str(uuid.uuid4()),
        "text":     str(data.get("text", "")).strip(),
        "priority": data.get("priority", "medium"),
        "start":    data.get("start", ""),
        "end":      data.get("end", ""),
    }
    if not msg["text"]:
        abort(400, "text is required")
    if msg["priority"] not in PRIORITY_ORDER:
        abort(400, "priority must be high, medium, or low")
    messages.append(msg)
    save_messages(messages)
    return jsonify(msg), 201


@app.put("/api/messages/<msg_id>")
def api_update_message(msg_id):
    data = request.get_json(force=True)
    messages = load_messages()
    for msg in messages:
        if msg["id"] == msg_id:
            msg["text"]     = str(data.get("text", msg["text"])).strip()
            msg["priority"] = data.get("priority", msg["priority"])
            msg["start"]    = data.get("start", msg["start"])
            msg["end"]      = data.get("end", msg["end"])
            if msg["priority"] not in PRIORITY_ORDER:
                abort(400, "priority must be high, medium, or low")
            save_messages(messages)
            return jsonify(msg)
    abort(404, "message not found")


@app.delete("/api/messages/<msg_id>")
def api_delete_message(msg_id):
    messages = load_messages()
    updated  = [m for m in messages if m["id"] != msg_id]
    if len(updated) == len(messages):
        abort(404, "message not found")
    save_messages(updated)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
