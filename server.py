from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

users = set()  # занятые ники

@app.route("/")
def home():
    return render_template("index.html")

@socketio.on("login")
def login(username):
    if username in users:
        emit("login_error", "Nickname already taken")
    else:
        users.add(username)
        emit("login_ok", username)

@socketio.on("message")
def handle(msg):
    send(msg, broadcast=True)

@socketio.on("disconnect")
def disconnect():
    # просто чистка (упрощённо)
    pass

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
