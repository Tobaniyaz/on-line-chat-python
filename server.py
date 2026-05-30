from flask import Flask, render_template
from flask_socketio import SocketIO, send

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/")
def home():
    return render_template("index.html")

@socketio.on("message")
def handle(msg):
    send(msg, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
