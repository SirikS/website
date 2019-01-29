import os
import random

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from functools import wraps
from cs50 import SQL
from passlib.apps import custom_app_context as pwd_context

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///instapet.db")


def apology(message, code=400):
    """
    Renders message as an apology to user.
    """
    def escape(s):
        """
        Escape special characters.
        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def errormessage(message, html_page, category=""):
    """
    Flashes an error message to the user.
    Takes the message and the html page as argument.
    Can take a category as optional argument.
    """
    flash(message, category)
    return render_template(html_page)


def h_login(username, password):
    """
    Logs the user in.
    """
    # query database for username
    rows = db.execute("SELECT * FROM accounts WHERE username = :username", username=username)

    # ensure username exists and password is correct
    if len(rows) != 1 or not pwd_context.verify(password, rows[0]["password"]):
        return False

    # remember which user has logged in
    session["user_id"] = rows[0]["userid"]

    # redirect user to home page
    return True


def username_taken(username):
    """
    Checks if username isnt allready taken
    """
    # if there is no row, it is not taken
    if len(db.execute("SELECT username FROM accounts WHERE username = :us", us=username)) != 0:
        return False
    return True


def h_register(username, password, email):
    """
    Inserts the new user into database
    Saves the session
    """
    # put the user into the database
    variable = db.execute("INSERT INTO accounts (username, password, email) VALUES (:us, :ps, :em)",
                          us=username, ps=password, em=email)
    # if it didnt work, something went wrong
    if not variable:
        return False

    # save the session
    session["user_id"] = variable
    return True


def h_upload(path, titel, caption, filename):
    """
    Saves picture, renames it and adjusts the database
    Returns the fotoid
    """
    # save the picture in the database
    opslaan = db.execute("INSERT INTO pictures (userid, path, titel, caption) VALUES (:id, :pt, :ti, :cp)",
                         id=session['user_id'], pt=path, ti=titel, cp=caption)
    # get the newly made fotoid
    fotoid = db.execute("SELECT fotoid FROM pictures WHERE userid = :usid AND path = :pt",
                        usid=session['user_id'], pt=path)[0]["fotoid"]

    # change the name in the correct folder, so it cant be there twice
    old_file = os.path.join("static/foto_upload", filename)

    # split the old file name to get the type of image (jpg, jpeg, png, etc)
    split_filename = filename.split('.')

    # rename the file
    new_name = str(fotoid) + "." + str(split_filename[-1])
    new_file = os.path.join("static/foto_upload", new_name)
    os.rename(old_file, new_file)

    # adjust the path in the database
    new_path = "/static/foto_upload/" + new_name
    db.execute("UPDATE pictures SET path = :pt WHERE userid = :id AND fotoid = :fid",
               id=session['user_id'], fid=fotoid, pt=new_path)
    return fotoid


def pf_upload(path, filename):
    """
    same as h_upload but then for profile pics
    But returns the path instead of fotoid
    """
    # save the picture in the database
    opslaan = db.execute("INSERT INTO profielfotos (path) VALUES (:path)", path=path)

    # get the newly made pfid
    fotoid = db.execute("SELECT pfid FROM profielfotos WHERE path = :pt", pt=path)[0]["pfid"]

    # change the name in the correct folder
    old_file = os.path.join("static/pf_upload", filename)

    # split the old file name to get the type of image (jpg, jpeg, png, etc)
    split_filename = filename.split('.')

    # rename the file
    new_name = str(fotoid) + "." + str(split_filename[-1])
    new_file = os.path.join("static/pf_upload", new_name)
    os.rename(old_file, new_file)

    # adjust the path in the database
    new_path = "/static/pf_upload/" + new_name
    db.execute("UPDATE profielfotos SET path = :pt WHERE pfid = :pfid", pt=new_path, pfid=fotoid)
    return new_path


def h_like(fotoid, userid, value):
    """
    Inserts the like into the database
    value = 1 stands for a like and value = 0 stands for a dislike
    """
    # checks if the like doesnt already exist
    if len(db.execute("SELECT * FROM beoordeeld WHERE userid = :userid AND fotoid = :fotoid",
                      fotoid=fotoid, userid=userid)) != 0:
        return False
    # insert the like/dislike
    db.execute("INSERT INTO beoordeeld (fotoid, userid, liked) VALUES (:fotoid, :userid, :liked)",
               fotoid=fotoid, userid=userid, liked=value)

    # changes the like/dislike in the total like/dislike count in the pictures database
    if value == '1':
        db.execute("UPDATE pictures SET totaallikes = totaallikes + 1 WHERE fotoid= :fotoid", fotoid=fotoid)
    else:
        db.execute("UPDATE pictures SET totaaldislikes = totaaldislikes + 1 WHERE fotoid= :fotoid", fotoid=fotoid)
    return True


def h_profile(name, profielfoto, beschrijving):
    """
    If a profile is changed, this function changes the database
    First checks if there is a profile yet, and if not all data must be given
    Else it changes the changed fields
    """
    # get the persons user id
    userid = session['user_id']

    # if no profile yet, make sure there is a name and profile picture
    if len(db.execute("SELECT * FROM profiel WHERE userid = :userid", userid=userid)) == 0:
        if not name:
            return False
        if not profielfoto:
            # if there is no profile pic, take our basic one
            profielfoto = "/static/pf_upload/23.png"
        # insert into database
        db.execute("INSERT INTO profiel (userid, name, profielfoto, beschrijving) VALUES (:userid, :name, :profielfoto, :beschrijving)",
                   userid=userid, name=name, profielfoto=profielfoto, beschrijving=beschrijving)
        return True

    # else if a value is not changed, get the old values
    if not name:
        name = db.execute("SELECT name FROM profiel WHERE userid = :userid", userid=userid)[0]['name']
    if not profielfoto:
        profielfoto = db.execute("SELECT profielfoto FROM profiel WHERE userid = :userid", userid=userid)[0]['profielfoto']
    if not beschrijving:
        beschrijving = db.execute("SELECT beschrijving FROM profiel WHERE userid = :userid", userid=userid)[0]['beschrijving']
    # adjust the database
    db.execute("UPDATE profiel SET name = :name, profielfoto = :profielfoto, beschrijving = :beschrijving WHERE userid = :userid",
               name=name, profielfoto=profielfoto, beschrijving=beschrijving, userid=userid)
    return True


def get_profiel(account):
    """
    Gets all data of an account
    """
    # try to get the userid of the account else the profile does not exist
    try:
        userid = db.execute("SELECT userid FROM accounts WHERE username= :username", username=account)[0]["userid"]
    except:
        return False
    # give the whole profile data back
    lijst = db.execute("SELECT * FROM profiel WHERE userid = :userid", userid=userid)[0]
    return lijst


def pfname(userid):
    """
    Returns the pf and name of an userid
    """
    profielfoto = db.execute("SELECT profielfoto FROM profiel WHERE userid = :userid", userid=userid)[0]["profielfoto"]
    name = db.execute("SELECT name FROM profiel WHERE userid = :userid", userid=userid)[0]["name"]
    return profielfoto, name


def h_follow(userid):
    """
    Inserts/deletes a follow dependent whether the follow already excists
    """
    # the user is the follower
    volgerid = session["user_id"]
    # you can not follow yourself
    if userid == volgerid:
        return False

    # Looks how many rows there are in the database
    rows = db.execute("SELECT * FROM volgers WHERE userid= :userid AND volgerid= :volgerid", userid=userid, volgerid=volgerid)

    # if no rows, add the follow
    if len(rows) == 0:
        db.execute("INSERT INTO volgers (userid, volgerid) VALUES (:userid, :volgerid)", userid=userid, volgerid=volgerid)
        db.execute("UPDATE profiel SET volgers = volgers + 1 WHERE userid = :userid", userid=userid)

    # if there is a row, unfollow
    elif len(rows) == 1:
        db.execute("DELETE FROM volgers WHERE userid = :userid AND volgerid= :volgerid", userid=userid, volgerid=volgerid)
        db.execute("UPDATE profiel SET volgers = volgers - 1 WHERE userid = :userid", userid=userid)

    # else, something gone wrong inside of the database
    else:
        return False
    return True


def volgcheck(profielnaam):
    """
    Returns a true or false statement depending on if the person is followed
    """
    userid = naamid(profielnaam)
    try:
        volgerid = session["user_id"]
    except:
        return False
    if len(db.execute("SELECT * FROM volgers WHERE userid = :userid AND volgerid = :volgerid", userid=userid, volgerid=volgerid)) == 1:
        return True
    return False


def login_required(f):
    """
    Decorate routes to require login.
    See: http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function


def naamid(username):
    """
    Returns the userid of a username
    """
    return db.execute("SELECT userid FROM accounts WHERE username= :username", username=username)[0]["userid"]


def idnaam(userid):
    """
    Returns the username of a userid
    """
    return db.execute("SELECT username FROM accounts WHERE userid= :userid", userid=userid)[0]["username"]


def random_fotoid():
    """
    Gets a random fotoid that has not been seen yet
    """
    userid = session["user_id"]

    beoordeeld = get_beoordeeld(userid)
    if not beoordeeld:
        beoordeeld = []
    # gets a list of pictures that are not their own's
    lijst = db.execute("SELECT fotoid FROM pictures WHERE userid != :userid AND fotoid NOT IN (:beoordeeld)",
                       userid=userid, beoordeeld=beoordeeld)

    # if empty, there are no photo's
    if lijst == []:
        return False

    # choose a random photo
    fotoid = random.choice(lijst)["fotoid"]
    return fotoid


def get_beoordeeld(userid):
    """
    returns all fotoid's of pictures that have been "beoordeed" yet
    """
    lijst = db.execute("SELECT fotoid FROM beoordeeld WHERE userid = :userid", userid=userid)
    return into_list(lijst)


def volger_fotoid():
    """
    same as random_fotoid but gets only pictures from followed accounts
    """
    # gets a list of
    userid = session["user_id"]
    volgend = get_volgend(userid)
    beoordeeld = get_beoordeeld(userid)

    # get the list of pictures to be seen
    lijst = db.execute("SELECT fotoid FROM pictures WHERE userid IN (:volgend) AND fotoid NOT IN (:beoordeeld)",
                       volgend=volgend, beoordeeld=beoordeeld)
    if not lijst:
        return False
    # choose a random one
    fotoid = random.choice(lijst)["fotoid"]
    return fotoid


def get_foto(fotoid):
    """
    Returns all variable's of a photo
    """
    try:
        return db.execute("SELECT * FROM pictures WHERE fotoid = :fotoid", fotoid=fotoid)[0]
    except:
        return False


def get_comments(fotoid):
    """
    Returns all comments on a photo
    """
    # get all the comments of a photo
    rows = db.execute("SELECT * FROM comments WHERE fotoid= :fotoid", fotoid=fotoid)
    comments = []

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
    """
    Returns a list of people they follow
    """
    volgenden = db.execute("SELECT userid FROM volgers WHERE volgerid = :volgerid", volgerid=userid)
    if not volgenden:
        return []
    return into_list(volgenden)


def get_gevolgd(userid):
    """
    Returns a list of people that he/she is followed by
    """
    volgenden = db.execute("SELECT volgerid FROM volgers WHERE userid = :userid", userid=userid)
    if not volgenden:
        return []
    return into_list(volgenden)


def get_persoonfotos(userid):
    """
    Gets all paths of an users photos
    """
    paths = db.execute("SELECT path FROM pictures WHERE userid = :userid", userid=userid)
    if not paths:
        return []
    return into_list(paths)


def get_likedfotos(userid):
    """
    Gets all paths of pictures a person liked
    """
    # Haalt de paden van alle gelikte foto's
    liked = db.execute("SELECT fotoid FROM beoordeeld WHERE userid = :userid AND liked = 1", userid=userid)
    if not liked:
        liked = []
    else:
        liked = into_list(liked)
    fotos = db.execute("SELECT path FROM pictures WHERE fotoid IN (:liked)", liked=liked)
    if not fotos:
        return []
    return into_list(fotos)


def post_comment(fotoid, comment):
    """
    Inserts the comment into the database
    """
    userid = session["user_id"]
    db.execute("INSERT INTO comments (fotoid, userid, comment) VALUES (:fotoid, :userid, :comment)",
               fotoid=fotoid, userid=userid, comment=comment)
    return True


def geldig(fotoid):
    """
    Checks if a photo excists
    """
    if db.execute("SELECT * FROM pictures WHERE fotoid= :fotoid", fotoid=fotoid):
        return True
    else:
        return False


def h_profielsearch(zoekopdracht):
    """
    Looks for all profiles containing a given name
    Then sets up the data for the html page
    """
    profiel_search = []
    # get all the profiles that match the search-term with their screenname out of the table
    names = db.execute("SELECT * FROM profiel WHERE UPPER(name)= :name", name=zoekopdracht.upper())

    # for every profile put the required info into a dictionary
    for name in names:
        profiel = {"account": idnaam(name['userid']), "user_id": name['userid'],
                   "profielnaam": name['name'], "profielfoto": name['profielfoto']}
        profiel_search.append(profiel)

    # get all the profiles that match the search-term with their screenname out of the table
    usernames = db.execute("SELECT * FROM accounts WHERE UPPER(username)= :name", name=zoekopdracht.upper())

    # for every profile put the required info into a dictionary
    for username in usernames:
        profiel = {"account": username["username"], "user_id": username['userid'],
                   "profielnaam": pfname(username['userid'])[1], "profielfoto": pfname(username['userid'])[0]}
        profiel_search.append(profiel)

    return profiel_search


def h_fotosearch(zoekopdracht):
    """
    Looks for all pictures containing a given search
    Then sets up the data for the html page
    """
    foto_search = []
    # get all the pictures that match with the searchterm
    fotos = db.execute("SELECT * FROM pictures WHERE UPPER(titel)= :ti", ti=zoekopdracht.upper())
    # for all pictures get the necessary information
    for foto in fotos:
        profiel = {"foto_id": foto['fotoid'], "path": foto['path'], "likes": foto["totaallikes"], "titel": foto["titel"]}
        foto_search.append(profiel)

    return foto_search


def h_gifje(path, title, caption):
    """
    Uploads a gif from the giphy API into the database
    """
    # uploads a path to the .gif file in the database and returns the fotoid
    userid = session["user_id"]
    opslaan = db.execute("INSERT INTO pictures (userid, path, titel, caption) VALUES (:userid, :path, :titel, :caption)",
                         userid=userid, path=path, titel=title, caption=caption)
    fotoid = db.execute("SELECT fotoid FROM pictures WHERE userid = :userid AND path = :path",
                        userid=userid, path=path)[0]["fotoid"]
    return fotoid


def info_door_path(path):
    """
    Gets all data of an picture with a specific path
    """
    info = {}
    fotos = db.execute("SELECT * FROM pictures WHERE path= :pt", pt=path)
    # per foto, insert the correct data into the dict
    for foto in fotos:
        info["path"] = path
        info["foto_id"] = foto["fotoid"]
        info["likes"] = foto["totaallikes"]
        info["titel"] = foto["titel"]
    return info


def prof_info_door_id(userid):
    """
    Gets all data of a profile using an userid
    """
    info = {}
    names = db.execute("SELECT * FROM profiel WHERE userid= :id", id=userid)
    # per profile, instert the correct data into the dict
    for name in names:
        info["account"] = idnaam(name['userid'])
        info['profielnaam'] = name['name']
        info['profielfoto'] = name['profielfoto']
    return info


def is_it_image(file):
    """
    Returns a boolean depending on the uploaded file
    """
    # get the last thing after the dot (jpg, png, etc) and make it lowercase
    type_file = str(file.filename.split('.')[-1]).lower()

    # list of most (if not all) types of image files
    image_files = ['tif', 'tiff', 'gif', 'jpeg', 'jpg', 'jif', 'jfif', 'jp2', 'jpx', 'j2k', 'j2x', 'fpx', 'pcd', 'png']

    # return apology if file is not an image
    if type_file not in image_files:
        return False
    else:
        return True


def lengte_comments(comments):
    """
    Returns specific values dependent on the amount of comments
    """
    if len(comments) == 1:
        return 'True'
    elif len(comments) == 0:
        return 'False'
    elif len(comments) == 2:
        return 'langer'
    else:
        return "nog_langer"


def foto_data(data):
    """
    Sets up data for the html page
    """
    userid = data["userid"]
    username = idnaam(userid)
    fotoid = data["fotoid"]
    foto = data['path']
    caption = data["caption"]
    titel = data["titel"]
    date = data["date"]
    likes = data["totaallikes"]
    return username, fotoid, foto, caption, titel, date, likes, userid


def into_list(lijst):
    """
    Changes data gotten by database into a normal list
    """
    if not lijst:
        return False
    # get the key
    for key in lijst[0]:
        key = key
    data = []
    # per dict, add to the list
    for x in range(len(lijst)):
        data.append(lijst[x][key])
    return data


def info(lijst, functie):
    """
    Loads data correct way for the template
    """
    # Gets all data of a path/userid in the correct way
    fotos = []
    if not lijst:
        return fotos
    for value in lijst:
        # loads the given function per user/path
        fotos.append(functie(value))
    return fotos


def namebio():
    """
    Returns the name and bio of a user
    """
    userid = session["user_id"]
    lijst = db.execute("SELECT * FROM profiel WHERE userid = :userid", userid=userid)[0]
    return lijst["name"], lijst["beschrijving"]
