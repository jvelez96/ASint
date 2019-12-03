from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/rooms")
def rooms():
    return render_template("rooms.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0',
            port=12345,
            debug=True)