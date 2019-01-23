from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import os
from urllib.parse import urlparse, parse_qs

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



@app.route("/")
def index():
    return render_template("index.html")



@app.route("/privacy")
def privacy():
    return render_template("privacy.html")



@app.route("/tos")
def tos():
    return render_template("tos.html")



@app.route("/support")
def support():
    return render_template("support.html")



@app.route("/profile", methods=["GET", "POST"])
@app.route("/profile/<username>", methods=["GET", "POST"])
@login_required
def profile(username = ''):
    # check if it is its own profile
    if username == idnaam(session["user_id"]):
        return redirect(url_for("profile"))

    # if no profile show his/her own
    if username == '':
        username = idnaam(session["user_id"])

    # get all profile attributes
    lijst = get_profiel(username)
    # if account is unvalid, go to their own page
    if not lijst:
        return redirect(url_for("profile"))

    # set all variables ready for template
    profielfoto = lijst["profielfoto"]
    profielnaam = lijst["name"]
    bio = lijst["beschrijving"]
    aantalvolgers = lijst["volgers"]

    # look if the profile is followed
    welvolg = volgcheck(username)

    # Laad de data voor de tabjes
    # lijst met dictionaries met info over de fotos
    p_fotos = []
    persoonlijkefotos = get_persoonfotos(naamid(username))
    for path in persoonlijkefotos:
        p_fotos.append(info_door_path(path))

    l_fotos = []
    likedfotos = get_likedfotos(naamid(username))
    for path in likedfotos:
        l_fotos.append(info_door_path(path))

    # lijst met dictionaries met info over de profielen
    p_profiel = []
    pack = get_volgend(naamid(username))
    for userid in pack:
        p_profiel.append(prof_info_door_id(userid))

    f_profiel = []
    following = get_gevolgd(naamid(username))
    for userid in following:
        p_profiel.append(prof_info_door_id(userid))
    return render_template("profile.html", userid = naamid(username), profielfoto= profielfoto, profielnaam= profielnaam,
                           aantalvolgers= aantalvolgers, bio= bio, welvolg= welvolg, p_fotos=p_fotos, l_fotos=l_fotos,
                           p_profiel=p_profiel, f_profiel=f_profiel)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # ensure username was submitted
        if not username:
            return apology("must provide username")

        # ensure password was submitted
        elif not password:
            return apology("must provide password")

        if h_login(username, password) == True:
            return redirect(url_for("home"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("index.html")



@app.route("/manage", methods=["GET", "POST"])
@login_required
def manage():
    if request.method == "POST":
        # als er een profielfoto geupload wordt dan moet je deze in het systeem zetten
        try:
            # the picture that is uploaded is saved in the folder foto_upload
            foto_upload = os.getcwd() + "/static/pf_upload"
            file = request.files['uploadfile']

            # if the file is not an image file, return an apology
            if is_it_image(file) == False:
                return apology('please submit an image file')

            # this is the path to the picture in the folder
            path= os.path.join(foto_upload, file.filename)

            file.save(path)
            filename = request.files['uploadfile'].filename
            profielfoto = pf_upload(path, filename)
        # anders is er geen profielfoto
        except:
            profielfoto = "NULL"
        # krijg ook de andere velden
        # TODO: CHECK DAT HET NIET TE LANG IS
        name = request.form.get("profielnaam")
        beschrijving = request.form.get("profielbio")
        # zet het in de database
        if h_profile(name, profielfoto, beschrijving):
            return redirect(url_for("profile"))

    return render_template("manage.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    # forget any user_id
    session.clear()

    if request.method == "POST":

        # temporaily save the
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("email")

        # ensure username was submitted
        if not username:
            return apology("must provide username")

        # ensure both passwords were submitted
        elif not password or not confirmation:
            return apology("must provide both passwords")

        # ensure passwords match
        elif confirmation != password:
            return apology("must fill in same password")

        elif not email:
            return apology("please enter email")

        if h_register(username, pwd_context.hash(password), email):
            return redirect(url_for("manage"))

    return render_template("index.html")



@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    # get a valid fotoid (not theirs or one they have "beoordeeld" yet)
    fotoid = random_fotoid()
    if not fotoid:
        return apology("geen foto's meer")

    # get all the data of a photo
    data = get_foto(fotoid)

    # get all values ready for template
    username = idnaam(data["userid"])
    fotoid = data["fotoid"]
    foto = data['path']
    caption = data["caption"]
    titel = data["titel"]
    date = data["date"]
    likes = data["totaallikes"]

    # get the uploader's profile pic and name
    profielfoto, naam = pfname(data["userid"])

    # also get the comments
    comments = get_comments(fotoid)
    aantalcomments = lengte_comments(comments)

    # TODO
    # Laad share mogelijkheden
    return render_template("home.html", aantalcomments= aantalcomments, foto= foto, caption= caption, fotoid= fotoid, titel= titel, date= date, profielfoto= profielfoto, naam= naam, comments= comments, accountnaam= username, likes = likes)



@app.route("/pack", methods=["GET", "POST"])
@login_required
def pack():
    # same as home() but then for the follow page
    # get a valid photo (not seen and by a person they follow)
    fotoid = volger_fotoid()
    if not fotoid:
        return apology("geen foto's meer")

    # get all data of a photo
    data = get_foto(fotoid)

    # get all values ready for template
    username = idnaam(data["userid"])
    fotoid = data["fotoid"]
    foto = data['path']
    caption = data["caption"]
    titel = data["titel"]
    date = data["date"]
    likes = data["totaallikes"]

    # get the uploaders profile pic and name
    profielfoto, naam = pfname(data["userid"])

    # also get the comments
    comments = get_comments(fotoid)
    aantalcomments = lengte_comments(comments)

    # TODO
    # Laad share mogelijkheden
    return render_template("pack.html", aantalcomments= aantalcomments, likes= likes, foto= foto, caption= caption, fotoid= fotoid, titel= titel, date= date, profielfoto= profielfoto, naam= naam, comments= comments, accountnaam= username)



@app.route("/like/<fotoid>/<direct>")
@login_required
def like(fotoid, direct = 'home'):
    # geef het een like
    userid = session["user_id"]
    if not h_like(fotoid, userid, '1'):
        return apology("You have liked/disliked this allready")
    return redirect(url_for(direct))



@app.route("/dislike/<fotoid>/<direct>")
@login_required
def dislike(fotoid, direct = 'home'):
    # geef het een dislike
    userid = session["user_id"]
    if not h_like(fotoid, userid, '0'):
        return apology("You have liked/disliked this allready")
    return redirect(url_for(direct))


# JOEY MOET DEZE NOG OP DE GOEDE MANIER MET JAVASCRIPT AANROEPEN
@app.route("/comment/<fotoid>", methods=["GET", "POST"])
@login_required
def comment(fotoid):
    # als het geen geldig fotoid is, dan apology
    if not geldig(fotoid):
        return apology("Fill in a valid photo-id")
    # krijg de fotoid en comment ready
    fotoid= int(fotoid)
    comment = request.form.get("uploadcomment")
    # post de comment
    post_comment(fotoid, comment)
    return redirect(url_for("/photo", fotoid= fotoid))



@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        # zorg dat de gebruiker een titel en een caption toevoegd
        title = request.form.get("titel")
        caption = request.form.get("caption")
        if not title or not caption:
            return apology("please enter a title and caption")
        # als er een foto geupload is run dan alles voor een foto
        try:
            file = request.files['uploadfile']

            # if the file is not an image file, return an apology
            if is_it_image(file) == False:
                return apology('please submit an image file')

            # the picture that is uploaded is saved in the folder foto_upload
            foto_upload = os.getcwd() + "/static/foto_upload"

            # this is the path to the picture in the folder
            path= os.path.join(foto_upload, file.filename)

            file.save(path)
            filename = request.files['uploadfile'].filename

            fotoid = h_upload(path, title, caption, filename)
            if fotoid:
                return redirect(url_for("photo", fotoid= fotoid))
            else:
                return apology("ging iets fout")

        # anders moet je het gifje uploaden
        except:
            path= request.form.get("gifje")

            # stop m in de database
            fotoid = h_gifje(path, title, caption)

            # als het is gelukt, ga naar de individuele pagina
            if fotoid:
                return redirect(url_for("photo", fotoid= fotoid))
            else:
                return apology("ging iets fout")

    return render_template("upload.html")



@app.route("/photo", methods=["GET", "POST"])
@app.route("/photo/<fotoid>", methods=["GET", "POST"])
@login_required
def photo(fotoid = False):
    # als er geen of een ongeldig fotoid is, geef apology
    if not fotoid:
        return apology("Fill in a photo-id")
    fotoid = int(fotoid)
    if not geldig(fotoid):
        return apology("Fill in a valid photo-id")

    # Vezamel alle data van de foto
    data = get_foto(fotoid)

    #ze de data klaar voor de template
    username = idnaam(data["userid"])
    fotoid = data["fotoid"]
    foto = data['path']
    caption = data["caption"]
    titel = data["titel"]
    date = data["date"]
    likes = data["totaallikes"]

    # get the uploaders profile pic and name
    profielfoto, naam = pfname(data["userid"])

    # also get the comments
    comments = get_comments(fotoid)
    aantalcomments = lengte_comments(comments)

    return render_template("photo.html", aantalcomments= aantalcomments, fotoid= fotoid, foto=foto, caption= caption, titel= titel, date= date, likes= likes, profielfoto= profielfoto, naam = naam, comments= comments)



@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    # clears sessin and goes back to index page
    session.clear()
    return redirect(url_for("index"))



# Dit is de functie die wordt aangeroepen in de 'neppe' refresh van de javascript. Hierin moet dus de volg functie worden aangeroepen.
@app.route('/follow/<userid>')
def follow(userid):
    # krijgt een gevolgd userid mee, en deze wordt in/uit de database gezet.
    userid = int(userid)
    if not h_follow(userid):
        return apology("You can not follow yourself")
    return "nothing"



@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    zoekopdracht = request.form.get("search")

    profiel_search = h_profielsearch(zoekopdracht)
    foto_search = h_fotosearch(zoekopdracht)

    print(profiel_search)

    # remove duplicates (if any) from searchresults for username and profilename
    profiel_search = [dict(t) for t in {tuple(d.items()) for d in profiel_search}]
    print(profiel_search)
    # tel het totaal aantal resultaten bij elkaar op
    aantalres = len(profiel_search) + len(foto_search)
    return render_template("search.html", profiel_search = profiel_search, foto_search = foto_search, zoekopdracht = zoekopdracht, aantalres = aantalres)
