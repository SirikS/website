import csv
import urllib.request

from flask import redirect, render_template, request, session
from flask_session import Session
from functools import wraps
from cs50 import SQL
from passlib.apps import custom_app_context as pwd_context
import os
import random
from urllib.parse import urlparse, parse_qs

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///instapet.db")



def apology(message, code=400):
    """Renders message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top= code, bottom= escape(message)), code


def h_login(username, password):
    # query database for username
    rows = db.execute("SELECT * FROM accounts WHERE username = :username", username= username)

    # ensure username exists and password is correct
    if len(rows) != 1 or not pwd_context.verify(password, rows[0]["password"]):
        return apology("iets werkt niet (niet gehasht ofz)")

    # remember which user has logged in
    session["user_id"] = rows[0]["userid"]

    # redirect user to home page
    return True


def h_register(username, password, email):
    variable = db.execute("INSERT INTO accounts (username, password, email) VALUES (:us, :ps, :em)",
                          us= username, ps= password, em= email)

    if not variable:
        return apology("Username already present")
    session["user_id"] = variable
    return True


def h_upload(path, titel, caption, filename):
    # sla de foto op in de database
    opslaan = db.execute("INSERT INTO pictures (userid, path, titel, caption) VALUES (:id, :pt, :ti, :cp)",
                          id=session['user_id'], pt= path, ti= titel, cp= caption)
    # haal de fotoid van de huidige foto op
    fotoid_list_dict = db.execute("SELECT fotoid FROM pictures WHERE userid = :usid AND path = :pt", usid=session['user_id'], pt=path)
    fotoid = fotoid_list_dict[0]["fotoid"]

    # verander de naam van de foto in de map foto_upload
    old_file = os.path.join("static/foto_upload", filename)
    new_name = str(fotoid) + ".jpg"
    new_file = os.path.join("static/foto_upload", new_name)

    os.rename(old_file, new_file)

    # maak een nieuw pad aan met de nieuwe naam
    new_path = "/static/foto_upload/" + new_name

    # voeg het nieuwe pad toe aan de database
    db.execute("UPDATE pictures SET path = :pt WHERE userid = :id AND fotoid = :fid",
                id=session['user_id'], fid=fotoid, pt=new_path)

    return True

def pf_upload(path, filename):
    opslaan = db.execute("INSERT INTO profielfotos (path) VALUES (:path)", path= path)
    fotoid_list_dict = db.execute("SELECT pfid FROM profielfotos WHERE path = :pt", pt=path)
    fotoid = fotoid_list_dict[0]["pfid"]

    # verander de naam van de foto in de map foto_upload
    old_file = os.path.join("static/pf_upload", filename)
    new_name = str(fotoid) + ".jpg"
    new_file = os.path.join("static/pf_upload", new_name)

    os.rename(old_file, new_file)

    # maak een nieuw pad aan met de nieuwe naam
    new_path = "/static/pf_upload/" + new_name

    # voeg het nieuwe pad toe aan de database
    db.execute("UPDATE profielfotos SET path = :pt WHERE pfid = :pfid", pt = new_path, pfid=fotoid)
    return new_path


def like(fotoid, userid, value):
    # value == 1 (like)
    # value == 0 (dislike)
    # inserts the like (or dislike) into the database
    db.execute("INSERT INTO beoordeeld (fotoid, userid, value) VALUES (:fotoid, :userid, :value)",
               fotoid= fotoid, userid= userid, value = value)
    # inserts the like/dislike into the total like/dislike count in foto database
    if value == 1:
        db.execute("UPDATE pictures SET totaallikes = totaallikes + 1 WHERE fotoid= :fotoid", fotoid= fotoid)
    else:
        db.execute("UPDATE pictures SET totaaldislikes = totaaldislikes + 1 WHERE fotoid= :fotoid", fotoid= fotoid)
    return True


def h_profile(name, profielfoto, beschrijving):
    # name = display name,  profielfoto = a link to the picture, beschrijving = profielbeschrijving
    userid = session['user_id']
    # if no profile yet, make sure there is a name and profile picture
    if len(db.execute("SELECT * FROM profiel WHERE userid = :userid", userid= userid)) == 0:
        if name == 'NULL':
            return apology("Must fill in a Name!")
        if profielfoto == 'NULL':
            profielfoto = "/static_pfupload/1.jpg"
        if beschrijving == "NULL":
            beschrijving = ""
        #insert into database
        db.execute("INSERT INTO profiel (userid, name, profielfoto, beschrijving) VALUES (:userid, :name, :profielfoto, :beschrijving)",
                   userid= userid, name= name, profielfoto= profielfoto, beschrijving= beschrijving)
        return True
    # else if a value is not changed, get the old values
    if name == 'NULL':
        name = db.execute("SELECT name FROM profiel WHERE userid = :userid", userid=userid)[0]['name']
    if profielfoto == 'NULL':
        profielfoto = db.execute("SELECT profielfoto FROM profiel WHERE userid = :userid", userid=userid)[0]['profielfoto']
    if beschrijving == 'NULL':
        beschrijving = db.execute("SELECT beschrijving FROM profiel WHERE userid = :userid", userid=userid)[0]['beschrijving']
    # adjust the database
    db.execute("UPDATE profiel SET name = :name, profielfoto = :profielfoto, beschrijving = :beschrijving WHERE userid = :userid",
               name= name, profielfoto = profielfoto, beschrijving = beschrijving, userid= userid)
    return True


def get_profiel(account):
    userid = db.execute("SELECT userid FROM accounts WHERE username = :username", username= account)[0]["userid"]
    lijst = db.execute("SELECT * FROM profiel WHERE userid = :userid", userid= userid)[0]
    return lijst


def pfname(userid):
    profielfoto = db.execute("SELECT profielfoto FROM profiel WHERE userid = :userid", userid = userid)[0]["profielfoto"]
    name = db.execute("SELECT name FROM profiel WHERE userid = :userid", userid = userid)[0]["name"]
    return profielfoto, name

def follow():
    volgerid = session["user_id"]
    url= request.url
    parsed = urlparse(url)
    user = parse_qs(parsed.query)['account'][0]
    userid = naamid(user)
    # Looks how many rows there are in the database
    rows = db.execute("SELECT * FROM volgers WHERE userid= :userid AND volgerid= :volgerid", userid= userid, volgerid= volgerid)
    # if no rows, add the follow
    if len(rows) == 0:
        db.execute("INSERT INTO volgers (userid, volgerid) VALUES (:userid, :volgerid", userid= userid, volgerid= volgerid)
        db.execute("UPDATE profiel SET volgers = volgers + 1 WHERE userid = :userid AND vogerid= :volgerid", userid= userid, volgerid= volgerid)
    # if 1 row, unfollow
    elif len(rows) == 1:
        db.execute("DELETE FROM volgers (userid, volgerid) VALUES (:userid, :volgerid", userid= userid, volgerid= volgerid)
        db.execute("UPDATE profiel SET volgers = volgers - 1 WHERE userid = :userid AND vogerid= :volgerid", userid= userid, volgerid= volgerid)
    # else something gone wrong inside the database
    else:
        return apology("Er ging iets fout in de database")
    return True


def volgcheck(profielnaam):
    userid = naamid(profielnaam)
    volgerid = session["user_id"]
    if len(db.execute("SELECT * FROM volgers WHERE userid = :userid AND volgerid = :volgerid", userid= userid, volgerid= volgerid)) == 1:
        return True
    return False


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

def naamid(username):
    return db.execute("SELECT userid FROM accounts WHERE username= :username", username = username)[0]["userid"]

def idnaam(userid):
    return db.execute("SELECT username FROM accounts WHERE userid= :userid", userid = userid)[0]["username"]


def random_fotoid():
    userid = session["user_id"]
    fotoid = 0
    while not check(fotoid):
        lijst = db.execute("SELECT fotoid FROM pictures WHERE userid != :userid", userid = userid)
        if lijst == []:
            return False
        fotoid = random.choice(lijst)["fotoid"]
    return fotoid

def check(fotoid):
    if fotoid == 0:
        return False
    userid = session["user_id"]
    rows = db.execute("SELECT * FROM beoordeeld WHERE userid = :userid AND fotoid = :fotoid", userid= userid, fotoid= fotoid)
    if len(rows) == 1:
        return False
    return True

def get_foto(fotoid):
    return db.execute("SELECT * FROM pictures WHERE fotoid = :fotoid", fotoid = fotoid)[0]


def get_comments(fotoid):
    rows = db.execute("SELECT * FROM comments WHERE fotoid= :fotoid", fotoid = fotoid)
    comments= []
    for row in range(len(rows)):
        comment = {}
        comment["berichtcomment"] = rows[row]["comment"]
        profielfoto, naam = pfname(rows[row]["userid"])
        comment["profielfotocomment"] = profielfoto
        comment["profielnaamcomment"] = naam
        comment["commentaccount"] = idnaam(rows[row]["userid"])
        comments.append(comment)
    return comments

def volger_fotoid():
    userid = session["user_id"]
    volgend = get_volgend(userid)
    fotoid = 0
    while not check(fotoid):
        print('ja')
        lijst = db.execute("SELECT fotoid FROM pictures WHERE userid IN (:volgend)", volgend = get_volgend(userid))
        if lijst == []:
            return False
        print(lijst)
        fotoid = random.choice(lijst)["fotoid"]
    print(fotoid)
    return fotoid


def get_volgend(userid):
    volgenden = db.execute("SELECT userid FROM volgers WHERE volgerid = :volgerid", volgerid= userid)
    volgend = []
    for x in range(len(volgenden)):
        volgend.append(volgenden[x]["userid"])
    return volgend
