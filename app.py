from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

import sqlite3

app = Flask(__name__)

# Connect to database and establish the db connection object
db = sqlite3.connect("sheets.db", check_same_thread=False)
# Connect cursor in db to make calls against
cur = db.cursor()
# Defining that the cursor should output dictionaries
cur.row_factory = sqlite3.Row

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Wrapper from https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Show errors
def errors(code):
    return render_template("error.html", code = code)

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return errors("Username was not submitted: 400")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return errors("Password was not submitted: 401")

        # Query database for username
        rows = cur.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),)).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return errors("Failed to login: 402")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
@app.route("/register", methods=["GET", "POST"])
def register():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return errors("Username was not submitted: 400")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return errors("Password was not submitted: 401")

        # Ensure password was confirmed
        elif request.form.get('password') != request.form.get('confirmation'):
            return errors("Confirmation password does not match password: 402")

        # Query database for username
        rows = cur.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),)).fetchall()

        # Check if username already exists
        if rows:
            return errors("Username already exists: 403")
        
        # hash password
        hash = generate_password_hash(request.form.get('password'))

        # Add data to db
        cur.execute('INSERT INTO users (username, password) VALUES (?,?)', (request.form.get('username'), hash))
        db.commit()

        # Send user to login
        return render_template("login.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template('register.html')

@app.route("/logout")
@login_required
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return render_template("login.html")

@app.route("/character")
@login_required
def character():
    return render_template("character.html")

@app.route("/new_character")
@login_required
def new_character():
    return render_template("new_character.html")