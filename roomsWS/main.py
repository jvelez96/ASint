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


@app.route('/roomsWS/campus', methods=['GET'])
def get_all_campus():
    return requests.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces').content

@app.route('/roomsWS/campus/<campus_id>', methods=['GET'])
def get_buildings_for_campus(campus_id):
    return requests.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces/'+campus_id).content

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

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201

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

@app.route("/getJsonFromFile/<filename>", methods=['GET'])
def get_json_response(filename):
    labels_dict = {}
    response_dict = {}
    try:
        with open(filename, 'r') as labels:
            labels_dict = json.load(labels)

        #response_dict[STATUS] = "true"
        response_dict["labels_mapping"] = labels_dict
        js_dump = json.dumps(response_dict)
        resp = Response(js_dump,status=200,\
                        mimetype='application/json')
    except FileNotFoundError as err:
        response_dict = {'error': 'file not found in server'}
        js_dump = json.dumps(response_dict)
        resp = Response(js_dump,status=500,\
                        mimetype='application/json')
    except RuntimeError as err:
        response_dict = {'error': 'error occured on server side. Please try again'}
        js_dump = json.dumps(response_dict)
        resp = Response(js_dump, status=500,\
                        mimetype='application/json')
    return resp


if __name__ == '__main__':
    app.run(debug=True,
            port=5001)
