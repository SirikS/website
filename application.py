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


@app.route("/history")
@login_required
def history():
    """Show history of transactions."""
    geschiedenis = db.execute("SELECT * FROM history WHERE userid = :userID", userID=session["user_id"])
    for x in range(len(geschiedenis)):
        geschiedenis[x]['price'] = usd(geschiedenis[x]['price'])
        geschiedenis[x]['total'] = usd(geschiedenis[x]['total'])
    print(geschiedenis)
    return render_template("history.html", history=geschiedenis)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username"
        password = request.form.get("password")

        # ensure username was submitted
        if not username:
            return apology("must provide username")

        # ensure password was submitted
        elif not password:
            return apology("must provide password")

        login(username, password)

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        quote = lookup(request.form.get("symbol"))
        if quote == None:
            return apology("Invalid symbol")
        return render_template("quote.html", name='Look at this awesome Quote!',
                               Name='Brand: ' + str(quote['name']),
                               Name2='Price: ' + usd(quote['price']))
    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    # forget any user_id
    session.clear()

    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # ensure password was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide both passwords")

        # ensure passwords match
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("must fill in same password")

        hash = pwd_context.hash(request.form.get("password"))
        variable = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                              username=request.form.get("username"), hash=hash)

        if not variable:
            return apology("Username already present")

        session["user_id"] = variable

        return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/balance", methods=["GET", "POST"])
@login_required
def balance():
    """Gives user money"""
    if request.method == "POST":
        hoeveelheid = request.form.get("hoeveelheid")
        try:
            hoeveelheid = float(hoeveelheid)
        except:
            return apology("must be a number")
        if not hoeveelheid >= 1:
            return apology("Must be at least 1")
        if hoeveelheid % 1 != 0:
            return apology("Must be whole dollars!")

        db.execute("UPDATE users SET cash = cash + :hoeveelheid WHERE id = :userID",
                   userID=session["user_id"], hoeveelheid=hoeveelheid)
        return render_template("balance.html", name=usd(hoeveelheid) + " was added to your account!",
                               name2="Your current balance is: " + usd(db.execute("SELECT cash FROM users WHERE id = :userID",
                                                                                  userID=session["user_id"])[0]['cash']))
        return apology("nog niet klaar")
    return render_template("balance.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    if request.method == "POST":
        symbool = request.form.get("symbol")
        quote = lookup(symbool)
        if quote == None:
            return apology("Invalid symbol")
        aantal = request.form.get("shares")
        try:
            aantal = (float(aantal))
        except:
            return apology("Give a number!")
        if aantal < 1:
            return apology("Sell at least 1 share")
        if aantal % 1 != 0:
            return apology("Sell whole shares!")
        aantal = int(aantal)
        prijs = (quote['price'] * float(aantal))
        try:
            oud = db.execute("SELECT aantal FROM stock WHERE userid = :userID AND symbool= :symbool",
                             userID=session["user_id"], symbool=symbool)[0]['aantal']
            print(oud)
            print(aantal)
            if oud < aantal:
                return apology("You cant sell this much!")
            if oud == aantal:
                db.execute("DELETE FROM stock WHERE userid = :userID AND symbool= :symbool",
                           userID=session["user_id"], symbool=symbool)
            else:
                db.execute("UPDATE stock SET aantal = :aantal WHERE userid = :userID AND symbool= :symbool",
                           userID=session["user_id"], aantal=(oud-aantal), symbool=symbool)
            db.execute("UPDATE users SET cash = cash + :totaalprijs WHERE id = :userID",
                       userID=session["user_id"], totaalprijs=prijs)
            db.execute("Insert INTO history (userid, symbol, amount, price, total) VALUES(:userid, :symbol, :amount, :price, :total)",
                       userid=session["user_id"], symbol=symbool, amount=-aantal, price=quote['price'], total=prijs)
        except:
            return apology("You cant sell if you dont own this stock!")
        merken = []
        oud = db.execute("SELECT symbool FROM stock WHERE userid = :userID AND aantal > 0", userID=session["user_id"])
        for x in range(len(oud)):
            merken.append(oud[x]['symbool'])
        return render_template("sell.html", name='Brand: ' + str(request.form.get('symbol')),
                               prijs='Price: ' + str(usd(quote['price'])),
                               aantal='Amount: ' + str(int(aantal)),
                               winst='Profit: ' + str(usd(prijs)),
                               geld='Balance left: ' + str(usd(db.execute("SELECT cash FROM users WHERE id = :userID",
                                                                          userID=session["user_id"])[0]['cash'])),
                               symbolen=merken)
    merken = []
    oud = db.execute("SELECT symbool FROM stock WHERE userid = :userID AND aantal > 0", userID=session["user_id"])
    for x in range(len(oud)):
        merken.append(oud[x]['symbool'])
    return render_template("sell.html", symbolen=merken)
