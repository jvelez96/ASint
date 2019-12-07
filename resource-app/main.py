from flask import Flask, render_template
from flask import json
from flask import Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/rooms")
def rooms():
    return render_template("rooms.html")

@app.route("/uploadFiles", methods=['POST'])


if __name__ == "__main__":
    app.run(host='0.0.0.0',
            port=5002,
            debug=False)