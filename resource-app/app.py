from flask import Flask, render_template
from flask import json
from flask import Response
from flask import redirect
from flask_cors import CORS

import requests

from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask import url_for



app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

from models import *
from forms import *


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}

@app.route("/")
def home():
    return render_template("index.html")

############################### Rooms WS integration ###############################################
@app.route("/rooms")
def rooms():
    resp = requests.get('http://127.0.0.1:5000/roomsWS/campus').content
    campus = json.loads(resp)
    #campus = requests.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces').content
    print(campus)
    return render_template("rooms.html", campus=campus)

@app.route("/rooms/buildings/<campus_id>")
def buildings_in_campus(campus_id):
    resp = requests.get('http://127.0.0.1:5000/roomsWS/campus/' + campus_id).content
    buildings = json.loads(resp)
    #Ainda falta tratar esta string json para apenas mostrar os edificios
    print(buildings)
    return render_template("buildings_in_campus.html", buildings=buildings)

@app.route("/rooms/floors/<building_id>")
def floors_in_building(building_id):
    resp = requests.get('http://127.0.0.1:5000/roomsWS/campus/' + building_id).content
    building = json.loads(resp)
    return render_template("floors_in_building.html", building=building)

@app.route("/rooms/<floor_id>")
def rooms_in_floor(floor_id):
    resp = requests.get('http://127.0.0.1:5000/roomsWS/campus/' + floor_id).content
    floor = json.loads(resp)
    return render_template("rooms_in_floor.html", floor=floor)

############################### Secretariats WS integration ###############################################
@app.route("/secretariats")
def secretariats():
    resp = requests.get('http://0.0.0.0:5003/secretariatWS/secretariats').content
    dict_secrs = json.loads(resp)
    secrs = dict_secrs["items"]
    return render_template("secretariats.html", secrs=secrs)

@app.route("/secretariats/<secr_id>")
def secretariat_info(secr_id):
    resp = requests.get('http://0.0.0.0:5003/secretariatWS/secretariats/' + secr_id).content
    secr = json.loads(resp)
    print("shit")
    print(secr)
    return render_template("secretariat_info.html", secr=secr)

@app.route("/secretariats/new", methods=['GET','POST'])
def new_secretariat():
    form = NewSecretariatForm()
    if form.validate_on_submit():
        api_url = 'http://0.0.0.0:5003/secretariatWS'
        #create json to send in post
        myjson = {
            'name': form.name.data,
            'location': form.location.data,
            'description': form.description.data,
            'opening_hours': form.opening_hours.data
        }
        #data = json.dumps(myjson)
        #print(data)
        print(myjson)
        #not working for some reason

        r = requests.post(url=api_url, json=myjson)
        resp= r.json()
        response = json.loads(r.content)
        print(resp)
        print(resp["id"])
        print("segundo id")
        print(response)

        #Enviar para a pagina da secretaria inserida lendo a response

        #tratar o caso de receber uma resposta de erro
        #if resp["error"]:
            #return render_template("new_secretariat.html", form=form)

        #fazer o redirect para a pagina da nova secretaria atraves do resp["id"] que nao esta a funcionar pelo tipo dessa variavel
        #return redirect(url_for(secretariats))
        return redirect('/secretariats')
    return render_template("new_secretariat.html", form=form)

@app.route("/secretariats/delete/<id>")
def delete_secretariat(id):
    api_url = 'http://0.0.0.0:5003/secretariatWS/secretariats/' + id
    x = requests.delete(api_url)
    return redirect("/secretariats")

if __name__== "__main__":
    app.run(host='0.0.0.0',
            port=5002,
            debug=True)