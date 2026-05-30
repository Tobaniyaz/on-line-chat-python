from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}

@app.route("/")
def home():
    return render_template("index.html")

@socketio.on("login")
def login(username):
    if username in users.values():
        emit("login_error", "Nickname already taken")
    else:
        users[request_sid()] = username
        emit("login_ok", username)
        emit("users_count", len(users), broadcast=True)

@socketio.on("message")
def handle(msg):
    sid = request_sid()
    name = users.get(sid, "Unknown")

    emit("message", {
        "name": name,
        "text": msg
    }, broadcast=True)

@socketio.on("disconnect")
def disconnect():
    sid = request_sid()
    if sid in users:
        del users[sid]
        emit("users_count", len(users), broadcast=True)

def request_sid():
    from flask import request
    return request.sid

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
