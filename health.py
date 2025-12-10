# health.py
from flask import Flask, jsonify
import os, time, json

app = Flask("health")

STATE_FILE = "store/state.json"

@app.route("/healthz")
def healthz():
    try:
        with open(STATE_FILE, "r") as f:
            s = json.load(f)
        return jsonify({
            "status": "ok",
            "seen_followers": len(s.get("seen_followers", [])),
            "queued_replies": len(s.get("queued_replies", [])) if s.get("queued_replies") else 0,
            "timestamp": int(time.time())
        })
    except Exception as e:
        return jsonify({"status":"error","error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("HEALTH_PORT", "8080")))
