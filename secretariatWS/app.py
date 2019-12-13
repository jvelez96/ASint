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
    if username == 'jvelez':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task


# Giving problems with special characters
@app.route('/secretariatWS/secretariats/<id>', methods=['GET'])
def get_secretariat(id):
    return jsonify(Secretariat.query.get_or_404(id).to_dict())


@app.route('/secretariatWS/secretariats', methods=['GET'])
def get_all_secretariats():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Secretariat.to_collection_dict(Secretariat.query, page, per_page, 'get_all_secretariats')
    return jsonify(data)

@app.route('/secretariatWS', methods=['POST'])
def create_secretariat():
    data = request.get_json() or {}
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
    return response

@app.route('/secretariatWS/secretariats/<id>', methods=['PUT'])
def update_secretariat(id):
    secr = Secretariat.query.get_or_404(id)
    data = request.get_json() or {}
    secr.from_dict(data, new_secretariat=False)
    db.session.commit()
    return jsonify(secr.to_dict())

@app.route('/secretariatWS/secretariats/<id>', methods=['DELETE'])
def delete_secretariat(id):
    secr = Secretariat.query.filter_by(id=id)
    if secr.first():
        secr.delete()
        db.session.commit()
    else:
        return bad_request('This secretariat does not exist.')

    return jsonify({'result': True})

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': task[0]})



@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
@auth.login_required
def get_tasks():
    return jsonify({'tasks': [make_public_task(task) for task in tasks]})



if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5003,
        debug=True)
