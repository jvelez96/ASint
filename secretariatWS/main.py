#!flask/bin/python
# coding=utf-8

from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
import requests
from flask import url_for
from flask import json
from flask import Response
from flask_cors import CORS

from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_httpauth import HTTPBasicAuth

from errors import *

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

from models import *


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Secretariat' : Secretariat}


auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    if username == 'asint-user':
        return app.config["WS_AUTH"]
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


# Giving problems with special characters
@app.route('/secretariatWS/secretariats/<id>', methods=['GET'])
def get_secretariat(id):
    return jsonify(Secretariat.query.get_or_404(id).to_dict())


@app.route('/secretariatWS/secretariats', methods=['GET'])
@auth.login_required
def get_all_secretariats():
    #adicionar a receçao do nmr da pagina a enviar
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Secretariat.to_collection_dict(Secretariat.query, page, per_page, 'get_all_secretariats')
    return jsonify(data)

@app.route('/secretariatWS', methods=['POST'])
@auth.login_required
def create_secretariat():
    data = request.get_json() or {}
    print(data)
    #verificar o tratamento de se a descriçao nao for precisa
    if 'name' not in data or 'location' not in data or 'description' not in data or 'opening_hours' not in data:
        return bad_request('Must include all fields')

    if Secretariat.query.filter_by(name=data['name']).first():
        return bad_request('This secretariat already exists.')

    secr = Secretariat()
    secr.from_dict(data, new_secretariat=True)
    db.session.add(secr)
    db.session.commit()

    response = jsonify(secr.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('get_secretariat', id=secr.id)
    #print(response)
    return response

@app.route('/secretariatWS/secretariats/<id>', methods=['PUT'])
@auth.login_required
def update_secretariat(id):
    secr = Secretariat.query.get_or_404(id)
    data = request.get_json() or {}

    s = Secretariat.query.filter_by(name=data['name']).first()

    if s and s.id != id:
        return bad_request('This secretariat already exists.')

    secr.from_dict(data, new_secretariat=False)

    db.session.commit()
    return jsonify(secr.to_dict())

@app.route('/secretariatWS/secretariats/<id>', methods=['DELETE'])
@auth.login_required
def delete_secretariat(id):
    secr = Secretariat.query.filter_by(id=id)
    if secr.first():
        secr.delete()
        db.session.commit()
    else:
        return bad_request('This secretariat does not exist.')

    return jsonify({'result': True})



if __name__ == '__main__':
    app.run(port=5003,
        debug=True)
