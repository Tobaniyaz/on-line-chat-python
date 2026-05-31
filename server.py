import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)


socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
)

users = {}  # sid -> username


@app.route("/")
def home():
    return render_template("index.html")


# 🔐 LOGIN
@socketio.on("login")
def login(username):
    username = (username or "").strip()

    if len(username) < 2:
        emit("login_error", "Nickname too short")
        return

    if username in users.values():
        emit("login_error", "Nickname already taken")
        return

    users[request.sid] = username

    emit("login_ok", {
        "name": username,
        "users": len(users)
    })

    emit("users_count", len(users), broadcast=True)


# 💬 MESSAGE
@socketio.on("message")
def message(msg):
    name = users.get(request.sid)
    if not name:
        return

    msg = (msg or "").strip()
    if not msg:
        return

    emit("message", {
        "name": name,
        "type": "text",
        "data": msg
    }, broadcast=True)


# 📎 FILE / IMAGE
@socketio.on("file")
def file_event(data):
    name = users.get(request.sid, "Unknown")

    emit("message", {
        "name": name,
        "type": data["type"],
        "data": data["data"],
        "filename": data.get("filename", "")
    }, broadcast=True)


# ⌨️ TYPING
@socketio.on("typing")
def typing(data):
    name = users.get(request.sid)
    if not name:
        return

    emit("typing", {
        "name": name,
        "state": data.get("state", False)
    }, broadcast=True, include_self=False)


# 👋 DISCONNECT
@socketio.on("disconnect")
def disconnect():
    if request.sid in users:
        del users[request.sid]

    emit("users_count", len(users), broadcast=True)


# 🚀 START (RENDER SAFE)
if __name__ == "__main__":
  socketio.run(
    app,
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 10000)),
    allow_unsafe_werkzeug=True
    )
