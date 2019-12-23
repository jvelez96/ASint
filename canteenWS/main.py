#!flask/bin/python
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
import requests
from flask import url_for
from flask import json
from flask import Response
from flask_cors import CORS

from flask_httpauth import HTTPBasicAuth

from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    if username == 'asint-user':
        return app.config["WS_AUTH"]
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


@app.route('/menus', methods=['GET'])
@auth.login_required
def get_all_menus():
    return requests.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/canteen').content



if __name__ == '__main__':
    app.run(port=5002,
            debug=True)