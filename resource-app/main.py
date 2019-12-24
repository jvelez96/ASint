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
import pymysql

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
from requests.auth import HTTPBasicAuth

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

global client

config = fenixedu.FenixEduConfiguration.fromConfigFile('fenixedu.ini')
client = fenixedu.FenixEduClient(config)

base_url = 'https://fenix.tecnico.ulisboa.pt/'
#redirect_to_me = 'https://asint2-262123.appspot.com/callback'
redirect_to_me = 'http://6960641f.ngrok.io/callback'

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

"""
db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')
"""

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

def get_connection():
    return pymysql.connect(user=db_user, password=db_password,
                              unix_socket=unix_socket, db=db_name, autocommit=True)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}



@app.route('/')
def login():
    logger.warning('WEB access to default login page')
    return render_template('login.html')

@app.route('/testdatabase')
def database_test():
    u = User.query.all()
    return render_template('test_database.html', users=u)


@app.route('/redirect', methods=["GET", "POST"])
def my_redirect():
    authorization_url = client.get_authentication_url()
    #authorization_url='https://fenix.tecnico.ulisboa.pt/oauth/userdialog?client_id='+client_id+'&redirect_uri='+redirect_to_me
    logger.warning('POST to authorization_url')
    return redirect(authorization_url)
    #return redirect(url)

@app.route('/callback', methods=["GET", "POST"])
def callback():
    config = fenixedu.FenixEduConfiguration.fromConfigFile('fenixedu.ini')
    client = fenixedu.FenixEduClient(config)

    if request.args.get('error'):
        return redirect(url_for('/'))

    logger.warning('GET to /callback endpoint')
    tokencode = request.args.get('code')
    logger.warning('code = ' + tokencode)

    fenixuser = client.get_user_by_code(tokencode)
    person = client.get_person(fenixuser)

    username=person['username']
    logger.warning('username = ' + username)

    token = fenixuser.access_token
    logger.warning('token = ' + token)
    session['access_token']=token
    session['username']=username

    try:
        u = User(username=username, email="rsilva@gmail.com", tokenn=token)
        db.session.add(u)
        db.session.commit()
    except Exception as e:
        logger.warning('user %s already exists', username)
        db.session.rollback()

    u = db.session.query(User).filter(User.username == username).first()
    u.tokenn = token
    db.session.commit()

    resp = make_response(redirect(url_for('home')))
    resp.set_cookie('username', username, secure=True)  #accessible in javascript
    return resp


@app.route('/home', methods=["GET", "POST"])
def home():
    logger.warning('WEB access to home page')
    return render_template("index.html")


@app.route("/logs")
def logs():
    F = open("app.log","r")
    logs = F.read().splitlines()
    return render_template("logs.html", logs=logs)


############################### Rooms WS integration ###############################################


@app.route("/campus")
def campus():
    try:
        resp = requests.get(roomsWS_url + '/roomsWS/campus', auth=('asint-user',app.config["WS_AUTH"])).content
    except requests.exceptions.RequestException as e:
        flash("Web Service not available!")
        return render_template("index.html")

    campus = json.loads(resp)
    print(campus)
    logger.warning('WEB access to campus page')
    return render_template("rooms.html", campus=campus)

@app.route("/location/<id>")
def location(id):
    try:
        resp = requests.get(roomsWS_url + '/roomsWS/campus/' + id, auth=('asint-user',app.config["WS_AUTH"])).content
    except requests.exceptions.RequestException as e:
        flash("Web Service not available!")
        return render_template("index.html")

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


############################### Secretariats WS integration ###############################################
@app.route("/secretariats")
def secretariats():
    try:
        resp = requests.get(secretariatWS_url + '/secretariatWS/secretariats', auth=('asint-user',app.config["WS_AUTH"])).content
    except requests.exceptions.RequestException as e:
        flash("Web Service not available!")
        return render_template("index.html")

    dict_secrs = json.loads(resp)
    secrs = dict_secrs["items"]
    logger.warning('Access to secretariatWS endpoint')
    return render_template("secretariats.html", secrs=secrs)

@app.route("/secretariats/<secr_id>")
def secretariat_info(secr_id):
    try:
        resp = requests.get(secretariatWS_url + '/secretariatWS/secretariats/' + secr_id, auth=('asint-user',app.config["WS_AUTH"])).content
    except requests.exceptions.RequestException as e:
        flash("Web Service not available!")
        return render_template("index.html")

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


            try:
                r = requests.post(url=api_url, json=myjson, auth=('asint-user',app.config["WS_AUTH"]))
            except requests.exceptions.RequestException as e:
                flash("Web Service not available!")
                return render_template("index.html")

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
                return render_template("new_secretariat.html", form=form)
            else:
                flash("Error!")
                return redirect(url_for('new_secretariat'))

    logger.warning('Access to secretariatWS new endpoint')
    return render_template("new_secretariat.html", form=form)

@app.route("/secretariats/delete/<id>")
def delete_secretariat(id):
    api_url = secretariatWS_url + '/secretariatWS/secretariats/' + id
    try:
        x = requests.delete(api_url, auth=('asint-user',app.config["WS_AUTH"]))
    except requests.exceptions.RequestException as e:
        flash("Web Service not available!")
        return render_template("index.html")

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
        try:
            r = requests.get(api_url, auth=('asint-user',app.config["WS_AUTH"])).content
        except requests.exceptions.RequestException as e:
            flash("Web Service not available!")
            return render_template("index.html")

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

            #r = requests.put(url=api_url, data=json.dumps(myjson))
            try:
                r = requests.put(api_url, json=myjson, auth=('asint-user',app.config["WS_AUTH"]))
            except requests.exceptions.RequestException as e:
                flash("Web Service not available!")
                return render_template("index.html")

            if r.status_code != 200:
                flash("Secretariat with that name already exists!")
                return render_template("new_secretariat.html", form=form)
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
    try:
        resp = requests.get(canteenWS_url + '/menus', auth=('asint-user',app.config["WS_AUTH"])).content
    except requests.exceptions.RequestException as e:
        flash("Web Service not available!")
        return render_template("index.html")

    print(resp)

    days = json.loads(resp)
    logger.warning('Access to canteenWS endpoint')
    return render_template("canteen.html", days=days)

if __name__== "__main__":
    app.run(debug=True)


#host='127.0.0.1',
            #port=8080,
