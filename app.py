"""
app.py

Backend server for the SF Self-Storage Manifest dashboard.
Serves the static dashboard files (index.html, data/) AND provides a
small REST API backed by SQLite for storing user-pinned locations
on the map. Pins persist permanently in a local file (pins.db).

Usage:
    pip install flask
    python app.py
Then open http://localhost:8000 (replaces the old
"python -m http.server 8000" command — use this instead from now on).
"""

import sqlite3
import os
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder=".", static_url_path="")

DB_PATH = "pins.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            label TEXT,
            note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")


@app.route("/api/pins", methods=["GET"])
def get_pins():
    conn = get_db()
    rows = conn.execute("SELECT * FROM pins ORDER BY created_at DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/pins", methods=["POST"])
def create_pin():
    data = request.get_json(silent=True) or {}
    lat = data.get("lat")
    lng = data.get("lng")
    label = (data.get("label") or "").strip()
    note = (data.get("note") or "").strip()

    if lat is None or lng is None:
        return jsonify({"error": "lat and lng are required"}), 400

    conn = get_db()
    cur = conn.execute(
        "INSERT INTO pins (lat, lng, label, note) VALUES (?, ?, ?, ?)",
        (lat, lng, label, note),
    )
    conn.commit()
    new_id = cur.lastrowid
    row = conn.execute("SELECT * FROM pins WHERE id = ?", (new_id,)).fetchone()
    conn.close()
    return jsonify(dict(row)), 201


@app.route("/api/pins/<int:pin_id>", methods=["DELETE"])
def delete_pin(pin_id):
    conn = get_db()
    conn.execute("DELETE FROM pins WHERE id = ?", (pin_id,))
    conn.commit()
    conn.close()
    return jsonify({"deleted": pin_id})


if __name__ == "__main__":
    init_db()
    print("Database ready: pins.db")
    print("Starting server at http://localhost:8000")
    app.run(host="0.0.0.0", port=8000, debug=True)