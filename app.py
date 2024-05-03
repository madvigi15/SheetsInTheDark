from flask import Flask, redirect, render_template, request, session
import sqlite3

app = Flask(__name__)

# Connect to database (or create if it doesn't exist)
db = sqlite3.connect("sheets.db")
# Connect cursor in db to make calls against
cur = db.cursor()

@app.route("/")
def index():
    return render_template("/index.html")