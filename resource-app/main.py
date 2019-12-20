from flask import Flask, render_template
from flask import request
from flask import json
from flask import Response
from flask import redirect
from flask_cors import CORS
from flask import flash
from flask import jsonify
from flask import session
from flask import make_response

import os

from flask_wtf.csrf import CSRFProtect

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

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

# create a file handler
handler = logging.FileHandler('app.log')
handler.setLevel(logging.WARNING)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)

# add the file handler to the logger
logger.addHandler(handler)

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
#csrf = CSRFProtect(app)
#csrf.init_app(app)
bootstrap = Bootstrap(app)

if os.getenv('GAE_INSTANCE'):
    roomsWS_url = 'https://rooms-dot-asint2-262123.appspot.com'
    canteenWS_url = 'https://canteen-dot-asint2-262123.appspot.com'
    secretariatWS_url = 'https://secretariat-dot-asint2-262123.appspot.com'
else:
    roomsWS_url = 'http://127.0.0.1:5001'
    canteenWS_url = 'http://127.0.0.1:5002'
    secretariatWS_url = 'http://127.0.0.1:5003'


redis_client = bmemcached.Client('redis-13711.c93.us-east-1-3.ec2.cloud.redislabs.com:13711', 'josemc.95@hotmail.com', '1995Jose!')

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
    logger.warning('WEB access to default login page')
    return render_template('login.html')

@app.route('/redirect', methods=["POST"])
def my_redirect():
    #url = client.get_authentication_url()
    authorization_url='https://fenix.tecnico.ulisboa.pt/oauth/userdialog?client_id='+client_id+'&redirect_uri=http://asint2-262123.appspot.com/callback'
    logger.warning('POST to authorization_url')
    return redirect(authorization_url)
    #return redirect(url)

@app.route('/callback', methods=["GET"])
def callback():
    logger.warning('GET to /callback endpoint')
    tokencode = request.args.get('code')
    logger.warning('code = ' + tokencode)

    fenixuser = client.get_user_by_code(tokencode)
    person = client.get_person(fenixuser)
    logger.warning('person = ' + person)

    username=person['username']

    token = fenixuser.access_token
    logger.warning('token = ' + token)
    session['access_token']=token
    session['username']=username

    #escreve username-token na memcache REDIS, expirando depois de 10 minutos
    logger.warning('inserting token')
    redis_client.set(username, token, 600)
    logger.warning('inserted')

    if(not checkToken(session['access_token'], session['username'])):
        authorization_url='https://fenix.tecnico.ulisboa.pt/oauth/userdialog?client_id='+client_id+'&redirect_uri=http://asint2-262123.appspot.com/callback'
        return redirect(authorization_url)

    resp = make_response(redirect(url_for('home')))
    resp.set_cookie('username', username, secure=True)  #accessible in javascript
    return resp


@app.route('/home', methods=["GET", "POST"])
def home():
    logger.warning('WEB access to home page')
    return render_template("index.html")

############################### Rooms WS integration ###############################################


@app.route("/campus")
def campus():
    resp = requests.get(roomsWS_url + '/roomsWS/campus').content
    campus = json.loads(resp)
    #campus = requests.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces').content
    print(campus)
    logger.warning('WEB access to campus page')
    return render_template("rooms.html", campus=campus)

@app.route("/location/<id>")
def location(id):
    resp = requests.get(roomsWS_url + '/roomsWS/campus/' + id).content
    r = json.loads(resp)
    type = r["type"]
    if type == 'CAMPUS':
        logger.warning('WEB access to campus page buildings_in_campus')
        return render_template("buildings_in_campus.html", buildings=r)
    elif type == 'BUILDING':
        logger.warning('WEB access to campus page floors_in_building')
        return render_template("floors_in_building.html", building=r)
    elif type == 'FLOOR':
        logger.warning('WEB access to campus page rooms_in_floor')
        return render_template("rooms_in_floor.html", floor=r)
    elif type == 'ROOM':
        logger.warning('WEB access to campus page room_details')
        return render_template("room_details.html", room=r)

    logger.warning('WEB access to campus page rooms')
    return render_template("rooms.html", campus=campus)


###############################  NOT USED ANYMORE #########################################################
@app.route("/rooms/buildings/<campus_id>")
def buildings_in_campus(campus_id):
    resp = requests.get(roomsWS_url + '/roomsWS/campus/' + campus_id).content
    buildings = json.loads(resp)
    #Ainda falta tratar esta string json para apenas mostrar os edificios
    print(buildings)
    logger.warning('WEB access to campus page buildings_in_campus')
    return render_template("buildings_in_campus.html", buildings=buildings)

@app.route("/rooms/floors/<building_id>")
def floors_in_building(building_id):
    resp = requests.get(roomsWS_url + '/roomsWS/campus/' + building_id).content
    building = json.loads(resp)
    logger.warning('WEB access to campus page floors_in_building')
    return render_template("floors_in_building.html", building=building)

@app.route("/rooms/<floor_id>")
def rooms_in_floor(floor_id):
    resp = requests.get(roomsWS_url + '/roomsWS/campus/' + floor_id).content
    floor = json.loads(resp)
    logger.warning('WEB access to campus page rooms_in_floor')
    return render_template("rooms_in_floor.html", floor=floor)

############################### Secretariats WS integration ###############################################
@app.route("/secretariats")
def secretariats():
    resp = requests.get(secretariatWS_url + '/secretariatWS/secretariats').content
    dict_secrs = json.loads(resp)
    secrs = dict_secrs["items"]
    logger.warning('Access to secretariatWS endpoint')
    return render_template("secretariats.html", secrs=secrs)

@app.route("/secretariats/<secr_id>")
def secretariat_info(secr_id):
    resp = requests.get(secretariatWS_url + '/secretariatWS/secretariats/' + secr_id).content
    secr = json.loads(resp)
    print("shit")
    print(secr)
    logger.warning('Access to secretariatWS id endpoint')
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

    logger.warning('Access to secretariatWS new endpoint')
    return render_template("new_secretariat.html", form=form)

@app.route("/secretariats/delete/<id>")
def delete_secretariat(id):
    api_url = secretariatWS_url + '/secretariatWS/secretariats/' + id
    x = requests.delete(api_url)
    flash("Secretariat deleted!")
    logger.warning('Access to secretariatWS delete id endpoint')
    return redirect("/secretariats")

#Edit secretariat with PUT method
@app.route("/secretariats/edit/<id>", methods=['GET', 'POST'])
def edit_secretariat(id):
    form = NewSecretariatForm()
    api_url = secretariatWS_url + '/secretariatWS/secretariats/' + id
    secr=[]

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

    """
    print(form.errors)

    if form.is_submitted():
        print("submitted")

    if form.validate():
        print("valid")

    print(form.errors)
    """

    if request.method == 'POST':
        if form.validate_on_submit():
            #create json to send in post
            myjson = {
                'name':form.name.data,
                'location':form.location.data,
                'description':form.description.data,
                'opening_hours':form.opening_hours.data
            }

            #r = requests.put(url=api_url, data=json.dumps(myjson))
            r = requests.put(api_url, json=myjson)

            if r.status_code != 200:
                flash("Bad Request!")
                return redirect(url_for('secretariats'))
            else:
                resp= r.json()
                print(resp)
                #print(resp)
                #url = '/secretariats/' + str(resp["id"])
                url = '/secretariats/' + str(resp["id"])
                #print(url)
                return redirect(url)

    logger.warning('Access to secretariatWS edit id endpoint')
    return render_template("edit_secretariat.html", form=form, secr=secr, error=form.errors)

###################################### CANTEEN WS #############################################

@app.route("/canteen")
def canteen():
    resp = requests.get(canteenWS_url + '/menus').content
    days = json.loads(resp)
    logger.warning('Access to canteenWS endpoint')
    return render_template("canteen.html", days=days)

if __name__== "__main__":
    app.run(debug=True)


#host='127.0.0.1',
            #port=8080,
