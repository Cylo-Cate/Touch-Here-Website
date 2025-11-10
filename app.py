from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
import os 
from flask import Flask, render_template , request, url_for, redirect , flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from db_models import DB, Usuarios,Musicas
from database import session
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

#Config Inicial
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

#Extensões[Login]
login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)

#Autentifição de Usuario // Criação de Conta
@app.route("/login", methods=["GET" ,"POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("senha")
        user = Usuarios.query.filter_by(email=email).first()#Se não achar , Retorna 'None'
        if user and user.check_password(password):
            login_user(user)
            flash("Login Efetuado! Seja Bem Vindo de Volta", 'success')
            return redirect(url_for('index'))
        else:
            flash("Email ou Senha incorretos!!", 'danger')
    return render_template('login.html')    
    
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return render_template(url_for("index"))
        
    if request.method == 'POST':
        nickname = request.form.get("nickname")
        email = request.form.get("email")
        password = request.form.get("password")
        
        account_created = Usuarios.query.filter_by(email=email).first()
        if account_created:
            flash("Essa Conta Já existe!!", 'danger')
            return render_template(url_for("register"))
            
        new_account = Usuarios(nome=nickname, email=email, senha=password, tipo_usuario='usuario')
        session.add(new_account)
        session.commit()
        flash('Conta Criada com Sucesso', 'success')
        return render_template(url_for("login"))
    return render_template('register.html')
    
#Logout
@app.route("/logout")
def logout():
    logout_user()
    flash('Desconectado', 'info')
    return redirect(url_for('index'))
    
#Home    
@app.route("/")
def index():
    return render_template("index.html", musicas=musicas, artistas=artistas)
    
#Favoritos
@app.route("/liked")
def liked():
      if current_user.is_authenticated:
          return render_template("liked.html", musicas=musicas)
      else:
          flash("Você precisa entrar para ver os seus favoritos!", 'danger')
          return redirect(url_for("index"))
#Playlist
@app.route("/playlist")
def playlist():
      if current_user.is_authenticated:
          return render_template("playlists.html", musicas=musicas)
      else:
          flash("Você precisa entrar para ver os seus favoritos!", 'danger')
          return redirect(url_for("index"))
    
        