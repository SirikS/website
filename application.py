from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

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
@login_required
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



# @app.route("/login", methods=["GET", "POST"])
# def login():
#     """Log user in."""

#     # forget any user_id
#     session.clear()

#     # if user reached route via POST (as by submitting a form via POST)
#     if request.method == "POST":

#         username = request.form.get("username")
#         password = request.form.get("password")

#         # ensure username was submitted
#         if not username:
#             return apology("must provide username")

#         # ensure password was submitted
#         elif not password:
#             return apology("must provide password")

#         login(username, password)

#     # else if user reached route via GET (as by clicking a link or via redirect)
#     else:
#         return render_template("index.html")


# @app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("index"))


@app.route("/beheer", methods=["GET", "POST"])
@login_required
def beheer():
    # Controle voor sessie gebruiker (Gebruiker moet ingelogt zijn)
    # Laad velden met aanpasbare gegevens
    # Vul velden met huidige data uit database. (Kan ook default waarde zijn.) Na drukken op 'bijwerken'
    # Controle voor correctheid (Velden niet leeg?, maximaal aantal karakters niet overschreden)
    # Aangepaste gegevens in database updaten
    # Doorverwijzen naar profielpagina
    return render_template("beheer.html")


# @app.route("/register", methods=["GET", "POST"])
# def register():
#     """Register user."""

#     # forget any user_id
#     session.clear()

#     if request.method == "POST":

#         # ensure username was submitted
#         if not request.form.get("username"):
#             return apology("must provide username")

#         # ensure password was submitted
#         elif not request.form.get("password"):
#             return apology("must provide password")

#         # ensure password was submitted
#         elif not request.form.get("confirmation"):
#             return apology("must provide both passwords")

#         # ensure passwords match
#         elif request.form.get("confirmation") != request.form.get("password"):
#             return apology("must fill in same password")

#         hash = pwd_context.hash(request.form.get("password"))
#         variable = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
#                               username=request.form.get("username"), hash=hash)

#         if not variable:
#             return apology("Username already present")

#         session["user_id"] = variable

#         return redirect(url_for("index"))
#     return render_template("index.html")


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
