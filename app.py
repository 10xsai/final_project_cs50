import os
import requests
from flask import Flask, render_template, redirect, request, session
import sqlite3
from helpers import login_required
#from flask_session importFA Session
from tempfile import mkdtemp

app = Flask(__name__)
app.secret_key = 'my secret key'

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
#Session(app)


conn = sqlite3.connect("users.sqlite", check_same_thread=False)
db = conn.cursor()
#db.execute("CREATE TABLE user (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT NOT NULL)")

@app.route('/')
@login_required
def index():
    photos = None
    return render_template('index.html', photos=photos)

@app.route('/add', methods=["POST", "GET"])
@login_required
def add():
    return render_template('add.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = db.execute("SELECT * FROM user WHERE username = ?", (username, )).fetchone()
        if user is None:
            return redirect("/login")
        if user[2] != password:
            return render_template("/login")
        session["user_id"]=user[0]
        return redirect("/")
    return render_template('login.html')

@app.route('/signup', methods=["GET", "POST"])
def signup():
    session.clear()
    if request.method == 'GET':
        status=200
        return render_template('signup.html', status=status)
    status = None
    username = request.form.get("username")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm-password")
    if password!=confirm_password:
        status=401
        return render_template("signup.html", status=status)
    users = db.execute("SELECT id FROM user WHERE username = ?", (username, )).fetchone()
    if users is not None:
        status=409
        return render_template("signup.html", status=status)
    db.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    user = db.execute('SELECT * FROM user where username= ?', (username, )).fetchone()
    session["user_id"]=user[1]
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')


if __name__ == "__main__":
    app.run()