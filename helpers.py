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
    # put the user into the database
    variable = db.execute("INSERT INTO accounts (username, password, email) VALUES (:us, :ps, :em)",
                          us= username, ps= password, em= email)
    # if it didnt work, the username is allready present
    if not variable:
        return apology("Username already present")
    # save the session
    session["user_id"] = variable
    return True



def h_upload(path, titel, caption, filename):
    # save the picture in the database
    opslaan = db.execute("INSERT INTO pictures (userid, path, titel, caption) VALUES (:id, :pt, :ti, :cp)",
                          id=session['user_id'], pt= path, ti= titel, cp= caption)
    # get the newly made fotoid
    fotoid = db.execute("SELECT fotoid FROM pictures WHERE userid = :usid AND path = :pt", usid=session['user_id'], pt=path)[0]["fotoid"]

    # change the name in the correct folder, so it cant be there twice
    old_file = os.path.join("static/foto_upload", filename)
    new_name = str(fotoid) + ".jpg"
    new_file = os.path.join("static/foto_upload", new_name)
    os.rename(old_file, new_file)

    # adjust the path in the database
    new_path = "/static/foto_upload/" + new_name
    db.execute("UPDATE pictures SET path = :pt WHERE userid = :id AND fotoid = :fid",
                id=session['user_id'], fid=fotoid, pt=new_path)
    return fotoid



def pf_upload(path, filename):
    # save the picture in the database
    opslaan = db.execute("INSERT INTO profielfotos (path) VALUES (:path)", path= path)

    # get the newly made pfid
    fotoid = db.execute("SELECT pfid FROM profielfotos WHERE path = :pt", pt=path)[0]["pfid"]

    # change the name in the correct folder
    old_file = os.path.join("static/pf_upload", filename)
    new_name = str(fotoid) + ".jpg"
    new_file = os.path.join("static/pf_upload", new_name)
    os.rename(old_file, new_file)

    # adjust the path in the database
    new_path = "/static/pf_upload/" + new_name
    db.execute("UPDATE profielfotos SET path = :pt WHERE pfid = :pfid", pt = new_path, pfid=fotoid)
    return new_path



def h_like(fotoid, userid, value):
    # value == 1 (like)
    # value == 0 (dislike)
    # inserts the like (or dislike) into the database
    db.execute("INSERT INTO beoordeeld (fotoid, userid, liked) VALUES (:fotoid, :userid, :liked)",
               fotoid= fotoid, userid= userid, liked = value)
    # inserts the like/dislike into the total like/dislike count in foto database
    if value == '1':
        db.execute("UPDATE pictures SET totaallikes = totaallikes + 1 WHERE fotoid= :fotoid", fotoid= fotoid)
    else:
        db.execute("UPDATE pictures SET totaaldislikes = totaaldislikes + 1 WHERE fotoid= :fotoid", fotoid= fotoid)
    return True



def h_profile(name, profielfoto, beschrijving):
    # get the persons user id
    userid = session['user_id']
    # if no profile yet, make sure there is a name and profile picture
    if len(db.execute("SELECT * FROM profiel WHERE userid = :userid", userid= userid)) == 0:
        if name == ' ':
            return apology("Must fill in a Name!")
        if profielfoto == ' ':
            profielfoto = "/static_pfupload/1.jpg"
        #insert into database
        db.execute("INSERT INTO profiel (userid, name, profielfoto, beschrijving) VALUES (:userid, :name, :profielfoto, :beschrijving)",
                   userid= userid, name= name, profielfoto= profielfoto, beschrijving= beschrijving)
        return True
    # else if a value is not changed, get the old values
    if not name:
        name = db.execute("SELECT name FROM profiel WHERE userid = :userid", userid=userid)[0]['name']
    if profielfoto == 'NULL':
        profielfoto = db.execute("SELECT profielfoto FROM profiel WHERE userid = :userid", userid=userid)[0]['profielfoto']
    if not beschrijving:
        beschrijving = db.execute("SELECT beschrijving FROM profiel WHERE userid = :userid", userid=userid)[0]['beschrijving']
    # adjust the database
    db.execute("UPDATE profiel SET name = :name, profielfoto = :profielfoto, beschrijving = :beschrijving WHERE userid = :userid",
               name= name, profielfoto = profielfoto, beschrijving = beschrijving, userid= userid)
    return True



def get_profiel(account):
    # try to get the userid of the account else the profile does not exist
    try:
        userid = db.execute("SELECT userid FROM accounts WHERE username= :username", username = account)[0]["userid"]
    except:
        return False
    # give the whole profile back
    lijst = db.execute("SELECT * FROM profiel WHERE userid = :userid", userid= userid)[0]
    return lijst



def pfname(userid):
    # gets the profile pic and name for example a comment
    profielfoto = db.execute("SELECT profielfoto FROM profiel WHERE userid = :userid", userid = userid)[0]["profielfoto"]
    name = db.execute("SELECT name FROM profiel WHERE userid = :userid", userid = userid)[0]["name"]
    return profielfoto, name



def h_follow(userid):
    # the user is the follower
    volgerid = session["user_id"]
    # the followed is the person who's profile is in the link

    # Looks how many rows there are in the database
    rows = db.execute("SELECT * FROM volgers WHERE userid= :userid AND volgerid= :volgerid", userid= userid, volgerid= volgerid)

    # if no rows, add the follow
    if len(rows) == 0:
        db.execute("INSERT INTO volgers (userid, volgerid) VALUES (:userid, :volgerid)", userid= userid, volgerid= volgerid)
        db.execute("UPDATE profiel SET volgers = volgers + 1 WHERE userid = :userid", userid= userid)

    # if there is a row, unfollow
    elif len(rows) == 1:
        db.execute("DELETE FROM volgers WHERE userid = :userid AND volgerid= :volgerid", userid= userid, volgerid= volgerid)
        db.execute("UPDATE profiel SET volgers = volgers - 1 WHERE userid = :userid", userid= userid)

    # else, something gone wrong inside of the database
    else:
        return False
    return True



def volgcheck(profielnaam):
    # returns a true or false statement depending on if the person is followed
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
    # returns the userid of a username
    return db.execute("SELECT userid FROM accounts WHERE username= :username", username = username)[0]["userid"]



def idnaam(userid):
    # returns the username of a userid
    return db.execute("SELECT username FROM accounts WHERE userid= :userid", userid = userid)[0]["username"]



def random_fotoid():
    # get a random photo
    userid = session["user_id"]

    beoordeeld = get_beoordeeld(userid)
    # gets a list of pictures that are not their own's
    lijst = db.execute("SELECT fotoid FROM pictures WHERE userid != :userid AND fotoid NOT IN (:beoordeeld)", userid = userid, beoordeeld = beoordeeld)

    # if empty, there are no photo's
    if lijst == []:
        return False

    # choose a random photo
    fotoid = random.choice(lijst)["fotoid"]
    return fotoid



def get_beoordeeld(userid):
    lijst = db.execute("SELECT fotoid FROM beoordeeld WHERE userid = :userid", userid= userid)
    beoordeeld = []
    for x in range(len(lijst)):
        beoordeeld.append(lijst[x]["fotoid"])
    return beoordeeld



def volger_fotoid():
    # same as random but gets only pictures from followed accounts
    userid = session["user_id"]
    volgend = get_volgend(userid)
    beoordeeld = get_beoordeeld(userid)

    # get the list of pictures to be seen
    lijst = db.execute("SELECT fotoid FROM pictures WHERE userid IN (:volgend) AND fotoid NOT IN (:beoordeeld)", volgend = volgend, beoordeeld= beoordeeld)
    if lijst == []:
        return False
    # choose a random one
    fotoid = random.choice(lijst)["fotoid"]
    return fotoid



def get_foto(fotoid):
    # returns all variable's of a photo
    try:
        return db.execute("SELECT * FROM pictures WHERE fotoid = :fotoid", fotoid = fotoid)[0]
    except:
        return False



def get_comments(fotoid):
    # get all comments of a photo
    rows = db.execute("SELECT * FROM comments WHERE fotoid= :fotoid", fotoid = fotoid)
    comments= []

    # for every comment, put the comment, profile pic, name and profile pic in the dict
    for row in range(len(rows)):
        comment = {}
        comment["berichtcomment"] = rows[row]["comment"]
        profielfoto, naam = pfname(rows[row]["userid"])
        comment["profielfotocomment"] = profielfoto
        comment["profielnaamcomment"] = naam
        comment["commentaccount"] = idnaam(rows[row]["userid"])
        comments.append(comment)
    return comments



def get_volgend(userid):
    # returns a list of people they follow
    volgenden = db.execute("SELECT userid FROM volgers WHERE volgerid = :volgerid", volgerid= userid)
    volgend = []
    for x in range(len(volgenden)):
        volgend.append(volgenden[x]["userid"])
    return volgend



def get_gevolgd(userid):
    # returns a list of people that he/she is followed by
    volgenden = db.execute("SELECT volgerid FROM volgers WHERE userid = :userid", userid= userid)
    volgend = []
    for x in range(len(volgenden)):
        volgend.append(volgenden[x]["volgerid"])
    return volgend



def get_persoonfotos(userid):
    paths = db.execute("SELECT path FROM pictures WHERE userid = :userid", userid = userid)
    for x in range(len(paths)):
        paths[x] = paths[x]["path"]
    return paths



def get_likedfotos(userid):
    liked = db.execute("SELECT fotoid FROM beoordeeld WHERE userid = :userid AND liked = 1", userid = userid)
    for x in range(len(liked)):
        liked[x] = liked[x]["fotoid"]
    fotos = db.execute("SELECT path FROM pictures WHERE fotoid IN (:liked)", liked= liked)
    for x in range(len(fotos)):
        fotos[x] = fotos[x]["path"]
    return fotos



def post_comment(fotoid, comment):
    userid = session["user_id"]
    db.execute("INSERT INTO comments (fotoid, userid, comment) VALUES (:fotoid, :userid, :comment)", fotoid= fotoid, userid= userid, comment= comment)
    return True



def geldig(fotoid):
    if db.execute("SELECT * FROM pictures WHERE fotoid= :fotoid", fotoid= fotoid):
        return True
    else:
        return False



def h_profielsearch(zoekopdracht):
    profiel_search = []

    names = db.execute("SELECT * FROM profiel WHERE name= :name", name= zoekopdracht)
    for name in names:
        profiel={}
        profiel["account"] = idnaam(name['userid'])
        profiel["user_id"] = name['userid']
        profiel['profielnaam'] = name['name']
        profiel['profielfoto'] = name['profielfoto']
        profiel_search.append(profiel)

    usernames = db.execute("SELECT * FROM accounts WHERE username= :name", name= zoekopdracht)
    for username in usernames:
        profiel={}
        profiel["user_id"] = username['userid']
        naam_foto = pfname(username['userid'])
        profiel['profielnaam'] = zoekopdracht
        profiel['profielfoto'] = naam_foto[0]
        profiel['account'] = zoekopdracht
        profiel_search.append(profiel)

    return profiel_search

def h_fotosearch(zoekopdracht):
    foto_search = []

    fotos= db.execute("SELECT * FROM pictures WHERE titel= :ti", ti= zoekopdracht)
    for foto in fotos:
        profiel={}
        profiel["foto_id"] = foto["fotoid"]
        profiel["path"] = foto["path"]
        profiel["likes"] = foto["totaallikes"]
        foto_search.append(profiel)

    return foto_search