import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# 👥 users
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

    # 👥 обновляем всем количество пользователей
    emit("users_count", len(users), broadcast=True)

    emit("login_ok", {
        "name": username,
        "users": len(users)
    })


# 💬 TEXT MESSAGE
@socketio.on("message")
def message(msg):
    from flask import request

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


# 📎 FILE / IMAGE (base64)
@socketio.on("file")
def file_event(data):
    from flask import request

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
    from flask import request

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


# 🚀 START SERVER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host="0.0.0.0", port=port)
