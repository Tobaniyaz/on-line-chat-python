from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import base64

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}

@app.route("/")
def home():
    return render_template("index.html")


@socketio.on("login")
def login(username):
    users[request.sid] = username
    emit("login_ok", username)


# 💬 text
@socketio.on("message")
def message(msg):
    name = users.get(request.sid, "Unknown")

    emit("message", {
        "name": name,
        "type": "text",
        "data": msg
    }, broadcast=True)


# 📎 file/image as base64 (НЕ СЕРВЕР ХРАНЕНИЕ)
@socketio.on("file")
def file(data):
    name = users.get(request.sid, "Unknown")

    emit("message", {
        "name": name,
        "type": data["type"],
        "data": data["data"],   # base64
        "filename": data["filename"]
    }, broadcast=True)
