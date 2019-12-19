from flask import Flask, render_template
from flask import request
from flask import json
from flask import Response
from flask import redirect
from flask_cors import CORS
from flask import flash
from flask import jsonify
from flask import session

from requests_oauthlib import OAuth2Session
import urllib3

from flask_bootstrap import Bootstrap

import requests

from config import Config

import fenixedu
import bmemcached

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from werkzeug.datastructures import MultiDict

from flask import url_for

config = fenixedu.FenixEduConfiguration.fromConfigFile('fenixedu.ini')
client = fenixedu.FenixEduClient(config)

base_url = 'https://fenix.tecnico.ulisboa.pt/'

app = Flask(__name__)
app.config.from_object(Config)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['REMEMBER_COOKIE_SECURE'] = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)
bootstrap = Bootstrap(app)
roomsWS_url = 'http://127.0.0.1:5000'
canteenWS_url = 'http://0.0.0.0:5002'
secretariatWS_url = 'http://0.0.0.0:5003'


redis_client = bmemcached.Client('memcached-18466.c3.eu-west-1-1.ec2.cloud.redislabs.com:18466', 'mc-KBY4m', 'otaT9lPXY9e3ppBnemshXeyIIvhBlAGL')

app.secret_key = 'tlxm7/1dt7a2UhkkE7BsOfEVi9EZMcnLETzzfUaDslyuNSH6MXeakcjFl7pnsvWiaDAGilRTbUwHywZ10f3loA=='
client_id='570015174623357'


from models import *
from forms import *

def checkToken(token, username):
    if redis_client.get(username)==token:
        return True
    else:
        return False


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/redirect', methods=["POST"])
def my_redirect():
    #url = client.get_authentication_url()
    authorization_url='https://fenix.tecnico.ulisboa.pt/oauth/userdialog?client_id='+client_id+'&redirect_uri=http://asint2-262123.appspot.com/callback'
    return redirect(authorization_url)
    #return redirect(url)

@app.route('/callback', methods=["GET"])
def callback():
    tokencode = request.args.get('code')

    fenixuser = client.get_user_by_code(tokencode)
    person = client.get_person(fenixuser)

    username=person['username']

    token = fenixuser.access_token
    session['access_token']=token
    session['username']=username

    #escreve username-token na memcache REDIS, expirando depois de 10 minutos
    redis_client.set(username, token, 600)

    if(not checkToken(session['access_token'], session['username'])):
        authorization_url='https://fenix.tecnico.ulisboa.pt/oauth/userdialog?client_id='+client_id+'&redirect_uri=http://asint2-262123.appspot.com/callback'
        return redirect(authorization_url)

    resp = make_response(redirect(url_for('home')))
    resp.set_cookie('username', username, secure=True)  #accessible in javascript
    #return resp
    return redirect(url_for('home'))

@app.route("/home")
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


    if request.method == 'POST':
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
            flash(r)
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
    app.run(host='127.0.0.1',
            port=8080,
            debug=True)