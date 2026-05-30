from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}  # sid -> username

@app.route("/")
def home():
    return render_template("index.html")


@socketio.on("login")
def login(username):
    sid = request.sid

    # защита от пустого ника
    if not username or username.strip() == "":
        emit("login_error", "Empty nickname")
        return

    username = username.strip()

    # проверка уникальности
    if username in users.values():
        emit("login_error", "Nickname already taken")
        return

    users[sid] = username

    emit("login_ok", username)
    emit("users_count", len(users), broadcast=True)


@socketio.on("message")
def handle(msg):
    sid = request.sid
    name = users.get(sid)

    # если нет ника — не даём писать
    if not name:
        emit("error", "You are not logged in")
        return

    emit("message", {
        "name": name,
        "text": msg
    }, broadcast=True)


@socketio.on("disconnect")
def disconnect():
    sid = request.sid

    if sid in users:
        del users[sid]

    emit("users_count", len(users), broadcast=True)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
