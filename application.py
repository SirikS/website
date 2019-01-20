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

    persoonlijkefotos = get_persoonfotos(naamid(username))
    likedfotos = get_likedfotos(naamid(username))

    #TODO
    #Laad foto's geplaatst door profiel
    #Laad gelikte foto's door profiel
    #Laad likes en dislikes op
    #Controle of gebruiker eigenaar is van profiel
    #Zo ja, laad bewerkknop voor profiel die redirect naar profiel beheerpagina.
    return render_template("profile.html", profielfoto= profielfoto, profielnaam= profielnaam, aantalvolgers= aantalvolgers, bio= bio, welvolg= welvolg, persoonlijkefotos= persoonlijkefotos, likedfotos= likedfotos)



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
        try:
            # the picture that is uploaded is saved in the folder foto_upload
            foto_upload = os.getcwd() + "/static/pf_upload"
            file = request.files['uploadfile']

            # this is the path to the picture in the folder
            path= os.path.join(foto_upload, file.filename)

            file.save(path)
            filename = request.files['uploadfile'].filename
            profielfoto = pf_upload(path, filename)
        except:
            profielfoto = "NULL"
        name = request.form.get("profielnaam")
        beschrijving = request.form.get("profielbio")
        if h_profile(name, profielfoto, beschrijving):
            return redirect(url_for("home"))

    # Controle voor sessie gebruiker (Gebruiker moet ingelogt zijn)
    # Laad velden met aanpasbare gegevens
    # Vul velden met huidige data uit database. (Kan ook default waarde zijn.) Na drukken op 'bijwerken'
    # Controle voor correctheid (Velden niet leeg?, maximaal aantal karakters niet overschreden)
    # Aangepaste gegevens in database updaten
    # Doorverwijzen naar profielpagina
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

    # get the uploader's profile pic and name
    profielfoto, naam = pfname(data["userid"])

    # also get the comments
    comments = get_comments(fotoid)
    # Laad like en dislike knop
    # Laad share mogelijkheden
    return render_template("home.html", foto= foto, caption= caption, fotoid= fotoid, titel= titel, date= date, profielfoto= profielfoto, naam= naam, comments= comments, accountnaam= username)



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

    # get the uploaders profile pic and name
    profielfoto, naam = pfname(data["userid"])

    # also get the comments
    comments = get_comments(fotoid)
    # Laad like en dislike knop
    # Laad share mogelijkheden
    # Laad like en dislike knop
    # Laad share mogelijkheden
    return render_template("pack.html", foto= foto, caption= caption, fotoid= fotoid, titel= titel, date= date, profielfoto= profielfoto, naam= naam, comments= comments, accountnaam= username)



@app.route("/like/<fotoid>")
@login_required
def like(fotoid):
    userid = session["user_id"]
    h_like(fotoid, userid, '1')
    return redirect(url_for("home"))



@app.route("/dislike/<fotoid>")
@login_required
def dislike(fotoid):
    userid = session["user_id"]
    h_like(fotoid, userid, '0')
    return redirect(url_for("home"))



# @app.route("/comment/<fotoid>", methods=["GET", "POST"])
# @login_required
# def comment(fotoid):
#     if not geldig(fotoid):
#         return apology("Fill in a valid photo-id")
#     fotoid= int(fotoid)
#     comment = request.form.get("uploadcomment")
#     post_comment(fotoid, comment)
#     return redirect(url_for("photo/" + str(fotoid)))



@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        # the picture that is uploaded is saved in the folder foto_upload
        foto_upload = os.getcwd() + "/static/foto_upload"
        file = request.files['uploadfile']

        # this is the path to the picture in the folder
        path= os.path.join(foto_upload, file.filename)

        file.save(path)
        filename = request.files['uploadfile'].filename

        # zorg dat de gebruiker een titel en een caption toevoegd
        title = request.form.get("titel")
        caption = request.form.get("caption")

        if not title or not caption:
            return apology("please enter a title and caption")

        if h_upload(path, title, caption, filename) == True:
            return redirect(url_for("home"))

    return render_template("upload.html")



# @app.route("/photo", methods=["GET", "POST"])
# @app.route("/photo/<fotoid>", methods=["GET", "POST"])
# @login_required
# def photo(fotoid = False):
#     if not fotoid:
#         return apology("Fill in a photo-id")
#     fotoid = int(fotoid)
#     if not geldig(fotoid):
#         return apology("Fill in a valid photo-id")
#     data = get_foto(fotoid)
#     return render_template("foto.html", data = data)



@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    # clears sessin and goes back to index page
    session.clear()
    return redirect(url_for("index"))



# Dit is de functie die wordt aangeroepen in de 'neppe' refresh van de javascript. Hierin moet dus de volg functie worden aangeroepen.
# Voor nu print hij even 'Hello' zodat ik in de frontend kon testen of het werkte. Als je flask runt en op een profiel nu op volg of ontvolg klikt, zie je in de terminal dat Hello wordt geprint.
@app.route('/followtest')
def followtest():
    # ff handimatig test of het werkt totdat ik een geldig userid krijg
    userid = int(1)
    if not h_follow(userid):
        return apology("ging iets fout in de database")
    return "nothing"