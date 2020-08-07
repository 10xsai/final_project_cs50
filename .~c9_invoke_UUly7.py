from flask import Flask, render_template, redirect, request

app = Flask(__name__)

people_list=["Adam", "Alex", "Aaron", "Ben", "Carl", "Dan", "David", "Edward", "Fred", "Frank", "George", "Hal", "Hank", "Ike", "John", "Jack", "Joe", "Larry", "Monte", "Matthew", "Mark", "Nathan", "Otto", "Paul", "Peter", "Roger", "Roger", "Steve", "Thomas", "Tim", "Ty", "Victor", "Walter"]
profile_data = {
    'image_url': 'http://www.goodmorningimagesdownload.com/wp-content/uploads/2017/11/Alone-300x187.gif',
    'user_name': 'Adam'
}
@app.route('/', methods=["POST", "GET"])
def index():
    return render_template('index.html')

@app.route('/people')
def people():
    return render_template('people.html', people=people_list)

@app.route('/profile')
def profile():
    return render_template('/profile.html', profile=profile_data)

@app.route('/account')
def account():
    pass

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect("/")
    return render_template('login.html')

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        return redirect("/")
    return render_template('signup.html')