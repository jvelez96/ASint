from flask import Flask, render_template
from flask import json
from flask import Response
from flask_cors import CORS
from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

import models

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/rooms")
def rooms():
    return render_template("rooms.html")


if __name__== "__main__":
    app.run(host='0.0.0.0',
            port=5002,
            debug=False)