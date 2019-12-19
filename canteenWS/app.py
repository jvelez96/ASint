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

app = Flask(__name__)
CORS(app)

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


@app.route('menus', methods=['GET'])
def get_all_campus():
    return requests.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/canteen').content

@app.route('/roomsWS/campus/<campus_id>', methods=['GET'])
def get_buildings_for_campus(campus_id):
    return requests.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces/'+campus_id).content



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
    app.run(port=5002,
            debug=True)