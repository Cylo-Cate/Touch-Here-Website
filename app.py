from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
import os 
from flask import Flask, render_template , request, url_for, redirect , flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from db_models import DB, Usuarios,Musicas
from functools import wraps
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

#Config Inicial
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

#Extensões[Login]
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)

@login_manager.user_loader #Facilita a Verificação do Usuario
def load_user(user_id):
    return Usuarios.query.get(int(user_id))

# Decorador para verificar se o usuário é admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Você precisa estar logado para acessar esta página", 'danger')
            return redirect(url_for('login'))
        if current_user.tipo_usuario != 'admin':
            flash("Acesso negado. Esta área é restrita para administradores", 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

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
        return render_template('index.html')
        
    if request.method == 'POST':
        nickname = request.form.get("nickname")
        email = request.form.get("email")
        password = request.form.get("password")
        
        account_created = Usuarios.query.filter_by(email=email).first()
        if account_created:
            flash("Essa Conta Já existe!!", 'danger')
            return render_template('register.html')
        
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_account = Usuarios(nome=nickname, email=email, senha=hashed_pw, tipo_usuario='usuario')
        session.add(new_account)
        session.commit()
        flash('Conta Criada com Sucesso', 'success')
        return render_template('login.html')
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
@login_required
def liked():
    return render_template("liked.html", musicas=musicas)
#Playlist
@app.route("/playlist")
@login_required
def playlist():
     return render_template("playlists.html", musicas=musicas)

@app.route("/profile")
@login_required
def profile():
    if current_user.is_authenticated:
        return render_template("profile.html", usuario=current_user)
    else:
        flash("Você Precisa entrar para Acessar essa Pagina", 'danger')