import os
import requests
from flask import Flask, render_template, redirect, request, session
import sqlite3
from helpers import login_required
from flask_session import Session
from tempfile import mkdtemp

app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


conn = sqlite3.connect("users.db")
db = conn.cursor()
#db.execute("CREATE TABLE user (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT NOT NULL)")

if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/add', methods=["POST", "GET"])
@login_required
def add():
    return render_template('add.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = db.execute("SELECT * FROM user WHERE email = :email", email=email).fetchone()
        if len(user) == 0:
            return redirect("/login")
        if user[0]["password"] != password:
            return render_template("/login")
        session["user_id"]=email
        return redirect("/")
    return render_template('login.html')

@app.route('/signup', methods=["GET", "POST"])
def signup():
    session.clear()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")
        if password!=confirm_password:
            return redirect("/signup")
        user = db.execute("SELECT email FROM user WHERE email = :email", email=email).fetchone()
        if len(user)==1:
            return redirect("/signup")
        db.execute("INSERT INTO user (email, password) VALUES (:email, :password)", email=email, password=password)
        db.execute("INSERT INTO profile (user_id, username, bio, hobbies, status) VALUES (:user_id, NULL, NULL, NULL, NULL)", user_id=email)
        session["user_id"]=user['email']
        return redirect("/")
    return render_template('signup.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')