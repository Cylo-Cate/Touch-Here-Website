from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
import os 
from flask import Flask, render_template , request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from db_models import DB, Usuarios,Musicas

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET = os.getenv("SECRET_KEY")

app = Flask(__name__)

admin = False

@app.route("/") 
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET" ,"POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("senha")

    if email == "adm@touch-here" and password == SECRET:
        admin == True
        return render_template("index.html", admin=True)

    