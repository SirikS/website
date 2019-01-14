import csv
import urllib.request

from flask import redirect, render_template, request, session
from functools import wraps

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")



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


def login(username, password):
    # query database for username
    rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)

    # ensure username exists and password is correct
    if len(rows) != 1 or not pwd_context.verify(password, rows[0]["hash"]):
        return apology("invalid username and/or password")

    # remember which user has logged in
    session["user_id"] = rows[0]["id"]

    # redirect user to home page
    return redirect(url_for("index"))


def register(username, password, name):
    return apology("todo")


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
