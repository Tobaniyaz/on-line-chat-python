from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

users = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    return {"url": f"/files/{file.filename}", "name": file.filename}

@app.route("/files/<name>")
def files(name):
    return send_from_directory(UPLOAD_FOLDER, name)


@socketio.on("login")
def login(username):
    users[request.sid] = username
    emit("login_ok", username)


@socketio.on("message")
def message(msg):
    name = users.get(request.sid, "Unknown")

    emit("message", {
        "name": name,
        "type": "text",
        "data": msg
    }, broadcast=True)


@socketio.on("file")
def file_msg(data):
    name = users.get(request.sid, "Unknown")

    emit("message", {
        "name": name,
        "type": data["type"],  # image / file
        "data": data["url"],
        "filename": data.get("filename", "")
    }, broadcast=True)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
