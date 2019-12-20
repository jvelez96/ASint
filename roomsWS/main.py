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



@app.route('/roomsWS/campus', methods=['GET'])
@auth.login_required
def get_all_campus():
    return requests.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces').content

@app.route('/roomsWS/campus/<campus_id>', methods=['GET'])
@auth.login_required
def get_buildings_for_campus(campus_id):
    return requests.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces/'+campus_id).content



@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True,
            port=5001)
