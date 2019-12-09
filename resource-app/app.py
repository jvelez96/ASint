from flask import Flask, render_template
from flask import json
from flask import Response
from flask_cors import CORS

import requests

from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate



app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

from models import *


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/rooms")
def rooms():
    campus = requests.get('http://127.0.0.1:5000/roomsWS/campus').content
    #campus = requests.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces').content
    print(campus)
    return render_template("rooms.html", campus=campus)


if __name__== "__main__":
    app.run(host='0.0.0.0',
            port=5002,
            debug=True)