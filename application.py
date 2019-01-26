import os

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
def index():
    """
    Renders the login/register screen
    """
    return render_template("index.html")


@app.route("/privacy")
def privacy():
    """
    Renders the privacy page
    """
    return render_template("privacy.html")


@app.route("/tos")
def tos():
    """
    Renders the terms of service page
    """
    return render_template("tos.html")


@app.route("/support")
def support():
    """
    Renders the support page
    """
    return render_template("support.html")


@app.route("/profile/", methods=["GET", "POST"])
@app.route("/profile/<username>", methods=["GET", "POST"])
@login_required
def profile(username=''):
    """
    Loads the profile of an account
    """
    eigenacc = False
    # check if it is its own profile
    if username == idnaam(session["user_id"]):
        return redirect(url_for("profile"))

    # if no profile show his/her own
    if username == '':
        username = idnaam(session["user_id"])
        eigenacc = True

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

    # load data for tabs
    p_fotos = []
    persoonlijkefotos = get_persoonfotos(naamid(username))
    for path in persoonlijkefotos:
        p_fotos.append(info_door_path(path))
    l_fotos = []
    likedfotos = get_likedfotos(naamid(username))
    for path in likedfotos:
        l_fotos.append(info_door_path(path))

    # get the data of pack and adopted by
    p_profiel = []
    pack = get_volgend(naamid(username))
    for userid in pack:
        p_profiel.append(prof_info_door_id(userid))
    f_profiel = []
    following = get_gevolgd(naamid(username))
    for userid in following:
        f_profiel.append(prof_info_door_id(userid))

    return render_template("profile.html", userid=naamid(username), profielfoto=profielfoto, profielnaam=profielnaam,
                           aantalvolgers=aantalvolgers, bio=bio, welvolg=welvolg, p_fotos=p_fotos, l_fotos=l_fotos,
                           p_profiel=p_profiel, f_profiel=f_profiel, eigenacc=eigenacc)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Check if login is correct
    Logs the user in
    """

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # ensure username was submitted
        if not username:
            flash('Please enter a username', 'login')
            return render_template("index.html")

        # ensure password was submitted
        elif not password:
            flash('Please enter a password', 'login')
            return render_template("index.html")

        if h_login(username, password) == True:
            return redirect(url_for("home"))
        else:
            flash('Wrong username or password', 'login')
            return render_template("index.html")
            # return apology("Wachtwoord en username komen niet overeen")

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("index.html")


@app.route("/manage", methods=["GET", "POST"])
@login_required
def manage():
    """
    Renders the manage page
    Uploads profile pic
    Adjusts the database
    """
    if request.method == "POST":
        # get name and bio
        name = request.form.get("profielnaam")
        beschrijving = request.form.get("profielbio")

        # ensure it is allowed
        if len(name) > 63:
            return apology("Your name is too long!")
        if len(beschrijving) > 255:
            return apology("Your bio is too long!")

        # if there is a profile pic, upload it
        try:
            # the picture that is uploaded is saved in the folder foto_upload
            foto_upload = os.getcwd() + "/static/pf_upload"
            file = request.files['uploadfile']

            # if the file is not an image file, return an apology
            if is_it_image(file) == False:
                return apology('please submit an image file')

            # this is the path to the picture in the folder
            path = os.path.join(foto_upload, file.filename)

            # TODO EMMA COMMENTS
            file.save(path)
            filename = request.files['uploadfile'].filename
            profielfoto = pf_upload(path, filename)
        # else there is no new profile pic
        except:
            profielfoto = "NULL"

        # insert into database
        if h_profile(name, profielfoto, beschrijving):
            return redirect(url_for("profile"))
        return apology("Something went wrong")

    return render_template("manage.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Checks the validity of a new account
    Inserts the user into the database
    """

    # forget any user_id
    session.clear()

    if request.method == "POST":

        # get all the inputs
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("email")

        # ensure username everything is submitted
        if not username:
            flash('Please enter a username', 'sign-up')
            return render_template("index.html")
        elif not password or not confirmation:
            flash('Please enter the password twice', 'sign-up')
            return render_template("index.html")
        elif not email:
            flash('Please enter an email', 'sign-up')
            return render_template("index.html")


        # check if the username is not already taken
        if username_taken(username) == False:
            flash('This username is taken', 'sign-up')
            return render_template("index.html")

        # ensure passwords match
        elif confirmation != password:
            flash('The two passwords do not match', 'sign-up')
            return render_template("index.html")

        # check if password is allowed
        if len(password) < 8:
            flash('The password must contain at least 8 characters', 'sign-up')
            return render_template("index.html")
        if not any([True for letter in password if letter.isupper()]):
            flash('The password must contain an upper-case letter', 'sign-up')
            return render_template("index.html")
        if not any([True for letter in password if letter.islower()]):
            flash('The password must contain a lower-case letter', 'sign-up')
            return render_template("index.html")
        if not any([True for letter in password if letter.isdigit()]):
            flash('The password must contain at least one number', 'sign-up')
            return render_template("index.html")

        # register the user in the database
        if h_register(username, pwd_context.hash(password), email):
            return redirect(url_for("manage"))
        else:
            flash('Something went wrong', 'sign-up')
            return render_template("index.html")

    return render_template("index.html")


@app.route("/home/", methods=["GET", "POST"])
@app.route("/home/<fotoid>", methods=["GET", "POST"])
@login_required
def home(fotoid = False):
    """
    Gets a random fotoid
    Shows all relevant data
    """
    # get a valid fotoid (not theirs or one they have "beoordeeld" yet)
    if not fotoid:
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
    userid= data["userid"]

    # get the uploader's profile pic and name
    profielfoto, naam = pfname(data["userid"])

    # also get the comments
    comments = get_comments(fotoid)
    aantalcomments = lengte_comments(comments)
    welvolg = volgcheck(username)

    # TODO
    # SHARE
    return render_template("home.html", userid=userid, welvolg=welvolg, aantalcomments=aantalcomments, foto=foto, caption=caption, fotoid=fotoid, titel=titel, date=date, profielfoto=profielfoto, naam=naam, comments=comments, accountnaam=username, likes=likes)


@app.route("/pack", methods=["GET", "POST"])
@app.route("/pack/<fotoid>", methods=["GET", "POST"])
@login_required
def pack(fotoid = False):
    """
    Gets a fotoid from the pack
    Shows all relevant data
    """

    # get a valid fotoid (not theirs or one they have "beoordeeld" yet)
    if not fotoid:
        fotoid = random_fotoid()
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
    userid= data["userid"]

    # get the uploaders profile pic and name
    profielfoto, naam = pfname(data["userid"])

    # also get the comments
    comments = get_comments(fotoid)
    aantalcomments = lengte_comments(comments)
    welvolg = volgcheck(username)

    # TODO
    # Laad share mogelijkheden
    return render_template("pack.html", userid=userid, welvolg=welvolg, aantalcomments=aantalcomments, likes=likes, foto=foto, caption=caption, fotoid=fotoid, titel=titel, date=date, profielfoto=profielfoto, naam=naam, comments=comments, accountnaam=username)


@app.route("/like/<fotoid>/<direct>")
@login_required
def like(fotoid, direct='home'):
    """
    Check if like doesnt already excist
    Registers the like in the database
    redirects to the coorect page
    """

    # check the fotoid
    if not geldig(fotoid):
        return apology("Fill in a valid photo-id")

    # insert the like
    userid = session["user_id"]
    if not h_like(fotoid, userid, '1'):
        return apology("You have liked/disliked this already")
    return redirect(url_for(direct))


@app.route("/dislike/<fotoid>/<direct>")
@login_required
def dislike(fotoid, direct='home'):
    """
    Check if dislike doesnt already excist
    Registers the dislike in the database
    Redirects to the correct page
    """

    # check the fotoid
    if not geldig(fotoid):
        return apology("Fill in a valid photo-id")

    # insert the dislike
    userid = session["user_id"]
    if not h_like(fotoid, userid, '0'):
        return apology("You have liked/disliked this already")
    return redirect(url_for(direct))


@app.route("/comment/<fotoid>/<direct>", methods=["GET", "POST"])
@login_required
def comment(fotoid, direct='home'):
    """
    Validates the photoid
    Registers the comment in the database
    Redirects to the correct page
    """
    # als het geen geldig fotoid is, dan apology
    if not geldig(fotoid):
        return apology("Fill in a valid photo-id")

    # get the comment
    comment = request.form.get("uploadcomment")

    # instert into database
    post_comment(fotoid, comment)
    return redirect(url_for(direct, fotoid=fotoid))


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """
    Renders the upload page
    Gets all user inputs and validates them
    Insert into database
    """
    if request.method == "POST":
        # get the user's input
        title = request.form.get("titel")
        caption = request.form.get("caption")

        # ensure every thing is alright
        if not title:
            return apology("please enter a title")
        elif not caption:
            return apology("please enter a caption")
        if len(title) > 255:
            return apology("Your title is too long!")
        if len(caption) > 255:
            return apology("Your caption is too long!")

        # if a file is uploaded, upload it
        try:
            file = request.files['uploadfile']

            # if the file is not an image file, return an apology
            if is_it_image(file) == False:
                return apology('please submit an image file')

            # the picture that is uploaded is saved in the folder foto_upload
            foto_upload = os.getcwd() + "/static/foto_upload"

            # this is the path to the picture in the folder
            path = os.path.join(foto_upload, file.filename)
            # TODO EMMA COMMENTS
            file.save(path)
            filename = request.files['uploadfile'].filename

            # upload into the database and redirect if all is good
            fotoid = h_upload(path, title, caption, filename)
            if fotoid:
                return redirect(url_for("photo", fotoid=fotoid))
            else:
                return apology("ging iets fout")

        except:
            # else a gif must be uploaded
            path = request.form.get("gifje")

            if not path:
                return apology("You must upload a file or seach a gif!")

            # insert into database
            fotoid = h_gifje(path, title, caption)

            # if all is good, redirect
            if fotoid:
                return redirect(url_for("photo", fotoid=fotoid))
            else:
                return apology("ging iets fout")

    return render_template("upload.html")


@app.route("/photo/", methods=["GET", "POST"])
@app.route("/photo/<fotoid>", methods=["GET", "POST"])
def photo(fotoid=False):
    """
    loads a photo with all data
    """
    # if unvalid fotoid apologize
    if not fotoid:
        return apology("Fill in a photo-id")
    if not geldig(fotoid):
        return apology("Fill in a valid photo-id")

    # get all data
    data = get_foto(fotoid)

    # Set up data for template
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
    welvolg = volgcheck(username)
    userid= data["userid"]

    return render_template("photo.html", userid=userid, welvolg=welvolg, aantalcomments=aantalcomments, fotoid=fotoid, foto=foto, caption=caption, titel=titel, date=date, likes=likes, profielfoto=profielfoto, naam=naam, comments=comments, accountnaam=username)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """
    Clears the session
    """

    # clears session and goes back to index page
    session.clear()
    return redirect(url_for("index"))


@app.route('/follow/<userid>')
def follow(userid):
    """
    Registers a follow/unfollow
    """
    # insert the follow/unfollow if it is not yourself
    if not h_follow(userid):
        return apology("You can not follow yourself")
    return "nothing"


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """
    Gets the search
    Get the data
    Give to template
    """
    # get the search
    zoekopdracht = request.form.get("search")

    # get the results
    profiel_search = h_profielsearch(zoekopdracht)
    foto_search = h_fotosearch(zoekopdracht)

    # remove duplicates (if any) from searchresults for username and profilename
    profiel_search = [dict(t) for t in {tuple(d.items()) for d in profiel_search}]

    # count the results
    aantalres = len(profiel_search) + len(foto_search)

    return render_template("search.html", profiel_search=profiel_search, foto_search=foto_search, zoekopdracht=zoekopdracht, aantalres=aantalres)
