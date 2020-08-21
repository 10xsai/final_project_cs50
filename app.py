import os
import sys
import requests
from flask import Flask, render_template, redirect, request, session
import sqlite3
import base64
from helpers import login_required
from tempfile import mkdtemp
from werkzeug import secure_filename

app = Flask(__name__)
app.secret_key = 'my secret key'

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["UPLOAD_FOLDER"] = "static/images"

ALLOWED_EXTENSIONS = {'jfif', 'jpg', 'jpeg', 'png', 'gif', 'tif', 'tiff'}

conn = sqlite3.connect("users.sqlite", check_same_thread=False)
db = conn.cursor()
#db.execute("CREATE TABLE user (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT NOT NULL)")
#db.execute("CREATE TABLE photos (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, photo BLOB NOT NULL)")

@app.route('/')
@login_required
def index():
    db.execute('SELECT photo from photos WHERE user_id=?', (session['user_id'], ))
    image_paths = db.fetchall()
    print(image_paths)
    return render_template('index.html', photos=image_paths)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/add', methods=["POST", "GET"])
@login_required
def add():
    if request.method=="GET":
        return render_template('add.html')
    f = request.files
    if 'file' not in f:
        return redirect(request.url)
    f = f['file']
    fname = f.filename

    if fname == '':
        return redirect(request.url)

    if not allowed_file(fname):
        return redirect(request.url)
            
    fname = secure_filename(fname)
    fpath = f"static/images/{session['user_id']}/{fname}"
    f.save(fpath)
    db.execute("INSERT INTO photos (user_id, photo) VALUES (?, ?)", (session['user_id'], fpath))
    conn.commit()
    return redirect('/')


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
    session["user_id"]=user[0]
    os.mkdir("static/images/"+str(user[0]))
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')


if __name__ == "__main__":
    app.run()