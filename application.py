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

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/")
@login_required
def index():
    cash = db.execute("SELECT cash FROM users WHERE id = :userID", userID=session["user_id"])[0]['cash']
    shares = db.execute("SELECT * FROM stock WHERE userid = :userID", userID=session["user_id"])
    print(shares)
    geldaandelen = 0
    for x in range(len(shares)):
        merk = shares[x]["symbool"]
        quote = lookup(merk)["price"]
        shares[x]["price"] = usd(quote)
        totaal = quote * float(shares[x]["aantal"])
        shares[x]["totaal"] = usd(totaal)
        geldaandelen += totaal
    samen = geldaandelen + cash
    samen = usd(samen)
    aandelen = usd(geldaandelen)
    return render_template("index.html",
                           cash=usd(cash),
                           shares=shares,
                           samen=samen,
                           aandelen=aandelen)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""
    if request.method == "POST":
        symbool = request.form.get("symbol")
        symbool = symbool.upper()
        quote = lookup(symbool)
        if quote == None:
            return apology("Invalid symbol")
        amount = request.form.get("shares")
        try:
            amount = (float(amount))
        except:
            return apology("Give a number!")
        if amount < 1:
            return apology("Must buy at least 1 share")
        if amount % 1 != 0:
            return apology("Buy whole shares!")
        geld = db.execute("SELECT cash FROM users WHERE id = :userID", userID=session["user_id"])
        print(geld)
        prijs = (quote['price'] * float(amount))
        if prijs > geld[0]['cash']:
            return apology("Not enough money")
        db.execute("UPDATE users SET cash = cash - :totaalprijs WHERE id = :userID", userID=session["user_id"], totaalprijs=prijs)
        try:
            oud = db.execute("SELECT aantal FROM stock WHERE userid = :userID AND symbool= :symbool",
                             userID=session["user_id"], symbool=symbool)[0]['aantal']
            db.execute("UPDATE stock SET aantal = :aantal WHERE userid = :userID AND symbool= :symbool",
                       userID=session["user_id"], aantal=oud+int(amount), symbool=symbool)
        except:
            db.execute("Insert INTO stock (userid, symbool, aantal) VALUES(:userid, :symbool, :aantal)",
                       userid=session["user_id"], symbool=symbool, aantal=int(amount))
        db.execute("Insert INTO history (userid, symbol, amount, price, total) VALUES(:userid, :symbol, :amount, :price, :total)",
                   userid=session["user_id"], symbol=symbool, amount=amount, price=quote['price'], total=prijs)
        return render_template("buy.html", name=str(symbool) + ' was bought for: ' + str(usd(prijs)),
                               cash='Balance left: ' + usd(db.execute("SELECT cash FROM users WHERE id = :userID", userID=session["user_id"])[0]['cash']))
    return render_template("buy.html")


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

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

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
