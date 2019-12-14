from flask import Flask, render_template
from flask import request
from flask import json
from flask import Response
from flask import redirect
from flask_cors import CORS
from flask import flash
from flask import jsonify

from flask_bootstrap import Bootstrap

import requests

from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from werkzeug.datastructures import MultiDict

from flask import url_for



app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)
bootstrap = Bootstrap(app)
roomsWS_url = 'http://127.0.0.1:5000'
canteenWS_url = 'http://0.0.0.0:5002'
secretariatWS_url = 'http://0.0.0.0:5003'


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
    resp = requests.get(roomsWS_url + '/roomsWS/campus').content
    campus = json.loads(resp)
    #campus = requests.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces').content
    print(campus)
    return render_template("rooms.html", campus=campus)

@app.route("/rooms/buildings/<campus_id>")
def buildings_in_campus(campus_id):
    resp = requests.get(roomsWS_url + '/roomsWS/campus/' + campus_id).content
    buildings = json.loads(resp)
    #Ainda falta tratar esta string json para apenas mostrar os edificios
    print(buildings)
    return render_template("buildings_in_campus.html", buildings=buildings)

@app.route("/rooms/floors/<building_id>")
def floors_in_building(building_id):
    resp = requests.get(roomsWS_url + '/roomsWS/campus/' + building_id).content
    building = json.loads(resp)
    return render_template("floors_in_building.html", building=building)

@app.route("/rooms/<floor_id>")
def rooms_in_floor(floor_id):
    resp = requests.get(roomsWS_url + '/roomsWS/campus/' + floor_id).content
    floor = json.loads(resp)
    return render_template("rooms_in_floor.html", floor=floor)

############################### Secretariats WS integration ###############################################
@app.route("/secretariats")
def secretariats():
    resp = requests.get(secretariatWS_url + '/secretariatWS/secretariats').content
    dict_secrs = json.loads(resp)
    secrs = dict_secrs["items"]
    return render_template("secretariats.html", secrs=secrs)

@app.route("/secretariats/<secr_id>")
def secretariat_info(secr_id):
    resp = requests.get(secretariatWS_url + '/secretariatWS/secretariats/' + secr_id).content
    secr = json.loads(resp)
    print("shit")
    print(secr)
    return render_template("secretariat_info.html", secr=secr)

@app.route("/secretariats/new", methods=['GET','POST'])
def new_secretariat():
    form = NewSecretariatForm()
    if form.validate_on_submit():
        api_url = secretariatWS_url + '/secretariatWS'
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
        if r.status_code == 201:
            resp= r.json()


            #Enviar para a pagina da secretaria inserida lendo a response

            #tratar o caso de receber uma resposta de erro
            #if resp["error"]:
                #return render_template("new_secretariat.html", form=form)

            #fazer o redirect para a pagina da nova secretaria atraves do resp["id"] que nao esta a funcionar pelo tipo dessa variavel
            #return redirect(url_for(secretariats))
            print(resp["id"])
            url= '/secretariats/' + str(resp["id"])
            print(url)
            return redirect(url)
        elif r.status_code == 400:
            flash("Error: Secretary already exists, or fields not filled!")
            return redirect(url_for('new_secretariat'))
        else:
            flash("Error!")
            return redirect(url_for('new_secretariat'))

    return render_template("new_secretariat.html", form=form)

@app.route("/secretariats/delete/<id>")
def delete_secretariat(id):
    api_url = secretariatWS_url + '/secretariatWS/secretariats/' + id
    x = requests.delete(api_url)
    flash("Secretariat deleted!")
    return redirect("/secretariats")

#Edit secretariat with PUT method
@app.route("/secretariats/edit/<id>", methods=['GET', 'POST'])
def edit_secretariat(id):
    form = NewSecretariatForm()
    api_url = secretariatWS_url + '/secretariatWS/secretariats/' + id
    print("url")
    print(api_url)

    if request.method == 'GET':

        r = requests.get(api_url).content
        secr = json.loads(r)

        #Verify if we got a response
        #if secr:

        name = secr["name"]
        location= secr["location"]
        description= secr["description"]
        opening_hours=secr["opening_hours"]

        #flash("That secretariat does not exist!")

        form = NewSecretariatForm(MultiDict([('name', name),('location', location),('description', description),('opening_hours', opening_hours)]))

    if request.method == 'POST':
        if form.validate_on_submit():
            #create json to send in post
            myjson = {
                'name':form.name.data,
                'location':form.location.data,
                'description':form.description.data,
                'opening_hours':form.opening_hours.data
            }
            print("json a enviar")
            print(myjson)

            #r = requests.put(url=api_url, data=json.dumps(myjson))
            r = requests.put(api_url, json=myjson)
            print("status code")
            print(r)
            print(r.status_code)

            if r.status_code != 200:
                print(r.text)
                flash("Bad Request!")
                return redirect(url_for('secretariats'))
            else:
                resp= r.json()
                #print(resp)
                #url = '/secretariats/' + str(resp["id"])
                url = '/secretariats/' + str(resp["id"])
                #print(url)
                return redirect(url)

    return render_template("edit_secretariat.html", form=form, secr=secr)

if __name__== "__main__":
    app.run(host='0.0.0.0',
            port=5002,
            debug=True)