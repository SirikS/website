from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import os

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
@login_required
def profile():
    # Laad profielfoto
    #Laad bio
    #Laad aantal volgers
    #Laad foto's geplaatst door profiel
    #Laad gelikte foto's door profiel
    #Laad likes en dislikes op
    #Controle of gebruiker eigenaar is van profiel
    #Zo ja, laad bewerkknop voor profiel die redirect naar profiel beheerpagina.
    return render_template("profile.html")



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
def beheer():
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
    # Controle voor sessie gebruiker (Gebruiker moet ingelogt zijn)
    # Laad random fotoID
    # Controle of gebruiker bericht al eens heeft beoordeeld (Loop door random fotoID's tot foto wordt gevonden, die nog niet is beoordeeld door gebruiker.)
    # Laad foto met bijbehorende caption, comments, profielfoto van plaatser, profielnaam van plaatser, titel, timestamp.
    # Laad like en dislike knop
    # Laad share mogelijkheden
    return render_template("home.html")
    #


@app.route("/pack", methods=["GET", "POST"])
@login_required
def pack():
    # Controle voor sessie gebruiker (Gebruiker moet ingelogt zijn)
    # Laad fotoID van profiel uit database met gevolgden door gebruiker (chronologische volgorde)
    # Controle of gebruiker bericht al eens heeft beoordeeld (Loop door random fotoID's tot foto wordt gevonden, die nog niet is beoordeeld door gebruiker.)
    # Laad foto met bijbehorende caption, comments, profielfoto van plaatser, profielnaam van plaatser, titel, timestamp.
    # Laad like en dislike knop
    # Laad share mogelijkheden
    return render_template("pack.html")

@app.route("/manage", methods=["GET", "POST"])
@login_required
def manage():
    return render_template("manage.html")


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        # the picture that is uploaded is saved in the folder foto_upload
        foto_upload = os.getcwd() + "/foto_upload"
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

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():

    session.clear()

    return redirect(url_for("index"))

