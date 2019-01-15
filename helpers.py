import csv
import urllib.request

from flask import redirect, render_template, request, session
from flask_session import Session
from functools import wraps
from cs50 import SQL
from passlib.apps import custom_app_context as pwd_context

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
    return render_template("apology.html", top=code, bottom=escape(message)), code


def h_login(username, password):
    # query database for username
    rows = db.execute("SELECT * FROM accounts WHERE username = :username", username=username)

    # ensure username exists and password is correct
    if len(rows) != 1 or not pwd_context.verify(password, rows[0]["password"]):
        return apology("iets werkt niet (niet gehasht ofz)")

    # remember which user has logged in
    session["user_id"] = rows[0]["userid"]

    # redirect user to home page
    return True


def h_register(username, password, email):
    variable = db.execute("INSERT INTO accounts (username, password, email) VALUES (:us, :ps, :em)",
                          us=username, ps=password, em=email)

    if not variable:
        return apology("Username already present")
    print(variable)
    session["user_id"] = variable
    return True


def upload(file, userid, titel, caption= ""):
    return apology("todo")


def like(fileid, userid):
    # vergeet niet ook de foto database aan te passen!
    return apology("todo")


def follow(userid, useridVOLGER):
    return apology("todo")


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
