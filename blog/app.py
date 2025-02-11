import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from dateutil.parser import parse

load_dotenv()

app = Flask(__name__)
client = MongoClient(os.getenv("MONGO_URL"))
app.db = client.Blog

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
myusername = os.getenv("myusername")
mypassword = os.getenv("mypassword")


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/blog' ,methods =["GET", "POST"])
def blog():
    print("Session before request:", session)
    if 'user' in session:
        user = session['user']  # Assign logged-in user's name to 'user'
    else:
        user = None  # No user logged in

    if request.method == "POST":
        if "username" in request.form and "password" in request.form:
            username = request.form.get('username')
            password = request.form.get('password')
            if username == myusername and password == mypassword:
                session['user'] = username
                return redirect(url_for("blog"))
            else:
                flash('Wrong Email or Password')
        elif "logout" in request.form:
            session.clear()
            return redirect(url_for("blog"))
        else:
            entry_content = request.form.get("content")
            formatted_date = datetime.datetime.today()
            app.db.entries.insert_one({"text": entry_content, "date":formatted_date})
            return redirect(url_for("blog"))
    
    entries = []

    for entry in app.db.entries.find({}).sort('date',-1):
        date_str = entry['date'].strftime("%a %b %d %I:%M %p %Y")
        entries.append((entry["text"], date_str))
    
    return render_template("blog.html", entries = entries, user=user)

if __name__ == '__main__':
    app.run()