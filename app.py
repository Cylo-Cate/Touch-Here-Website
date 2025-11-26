import os
from flask import Flask, render_template, request, url_for, redirect, flash, jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from database import init_db
from db_models import db, Usuarios, Musicas, Artistas, Genero, Albuns, Playlist, PlaylistMusicas, Favoritos
from functools import wraps
from yt_dlp import YoutubeDL

# CONFIGURAÇÕES INICIAIS
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializar DB
init_db(app)

# Extensões
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# LOGIN MANAGER
@login_manager.user_loader
def load_user(user_id):
    return Usuarios.query.get(int(user_id))


#Admin - Decorador
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Faça login primeiro", "warning")
            return redirect(url_for("login"))
        if not current_user.is_admin:
            flash("Acesso negado. Apenas administradores!", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated


#Login e Registro
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get("email")
        senha = request.form.get("senha")

        user = Usuarios.query.filter_by(email=email).first()

        if user and user.check_password(senha):
            login_user(user)
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("index"))
        else:
            flash("Email ou senha inválidos.", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == 'POST':
        nome = request.form.get("nickname")
        email = request.form.get("email")
        senha = request.form.get("password")

        if Usuarios.query.filter_by(email=email).first():
            flash("Este e-mail já está cadastrado!", "danger")
            return render_template("register.html")

        novo = Usuarios(
            nome=nome,
            email=email,
            tipo_usuario="usuario"
        )
        novo.set_password(senha)

        db.session.add(novo)
        db.session.commit()
        flash("Conta criada com sucesso!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da conta.", "info")
    return redirect(url_for("index"))


#Home
@app.route("/")
def index():
    musicas = Musicas.query.all()
    artistas = Artistas.query.all()

    return render_template(
        "index.html",
        musicas=musicas,
        artistas=artistas,
        usuario=current_user if current_user.is_authenticated else None
    )


#Area do Admin
@app.route("/admin")
@login_required
@admin_required
def admin():
    return render_template(
        "admin_home.html",
        total_usuarios=Usuarios.query.count(),
        total_musicas=Musicas.query.count(),
        total_artistas=Artistas.query.count(),
        total_albuns=Albuns.query.count()
    )


#Musicas - Crud

@app.route("/admin/musicas")
@login_required
@admin_required
def crud_musicas():
    return render_template(
        "crud_music.html",
        musicas=Musicas.query.all(),
        artistas=Artistas.query.all(),
        generos=Genero.query.all(),
        albuns=Albuns.query.all()
    )


def get_or_create_artista(nome_artista):
    artista = Artistas.query.filter_by(nome=nome_artista).first()
    if not artista:
        artista = Artistas(nome=nome_artista)
        db.session.add(artista)
        db.session.commit()
    return artista


def get_or_create_genero(nome_genero):
    genero = Genero.query.filter_by(tipo=nome_genero).first()
    if not genero:
        genero = Genero(tipo=nome_genero)
        db.session.add(genero)
        db.session.commit()
    return genero


def get_or_create_album(titulo_album, artista_id):
    if not titulo_album or titulo_album.strip() == "":
        return None
    
    album = Albuns.query.filter_by(titulo=titulo_album).first()
    if not album:
        album = Albuns(titulo=titulo_album, artista_id=artista_id)
        db.session.add(album)
        db.session.commit()
    return album


@app.route("/admin/musicas/adicionar", methods=["POST"])
@login_required
@admin_required
def adicionar_musica():
    try:
        titulo = request.form.get("titulo")
        artista_nome = request.form.get("artista")
        genero_nome = request.form.get("genero")
        album_titulo = request.form.get("album")
        url = request.form.get("url")

        if not titulo or not artista_nome or not genero_nome:
            flash("Preencha título, artista e gênero!", "danger")
            return redirect(url_for("crud_musicas"))

        # Buscar ou criar artista
        artista = get_or_create_artista(artista_nome.strip())
        
        # Buscar ou criar gênero
        genero = get_or_create_genero(genero_nome.strip())
        
        # Buscar ou criar álbum (se fornecido)
        album = None
        if album_titulo and album_titulo.strip() != "":
            album = get_or_create_album(album_titulo.strip(), artista.id)

        nova_musica = Musicas(
            titulo=titulo.strip(),
            artista_id=artista.id,
            genero_id=genero.id,
            album_id=album.id if album else None,
            caminho_pasta="",
        )

        db.session.add(nova_musica)
        db.session.commit()

    #Config do Audio do Youtube
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'Touch-Here-Website/static/musics/{nova_musica.id}.%(ext)s', # Destino e Nome do Arquivo
            'nocheckcertificate': True,
        }
    #Baixa a Musica
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        nova_musica.caminho_pasta = f"Touch-Here-Website/static/musics/{nova_musica.id}.webm"
        db.session.commit()    
        flash("Música adicionada com sucesso!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao adicionar música: {str(e)}", "danger")

    return redirect(url_for("crud_musicas"))


@app.route("/admin/musicas/editar/<int:musica_id>", methods=["POST"])
@login_required
@admin_required
def editar_musica(musica_id):
    try:
        musica = Musicas.query.get_or_404(musica_id)
        
        titulo = request.form.get("titulo")
        artista_nome = request.form.get("artista")
        genero_nome = request.form.get("genero")
        album_titulo = request.form.get("album")

        if not titulo or not artista_nome or not genero_nome:
            flash("Preencha título, artista e gênero!", "danger")
            return redirect(url_for("crud_musicas"))

        # Buscar ou criar artista
        artista = get_or_create_artista(artista_nome.strip())
        
        # Buscar ou criar gênero
        genero = get_or_create_genero(genero_nome.strip())
        
        # Buscar ou criar álbum(Caso Necessario)
        album = None
        if album_titulo and album_titulo.strip() != "":
            album = get_or_create_album(album_titulo.strip(), artista.id)

        musica.titulo = titulo.strip()
        musica.artista_id = artista.id
        musica.genero_id = genero.id
        musica.album_id = album.id if album else None

        db.session.commit()
        flash("Música atualizada com sucesso!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao editar música: {str(e)}", "danger")

    return redirect(url_for("crud_musicas"))


@app.route("/admin/musicas/deletar/<int:musica_id>")
@login_required
@admin_required
def deletar_musica(musica_id):
    try:
        musica = Musicas.query.get_or_404(musica_id)
        if PlaylistMusicas.query.filter_by(musica_id=musica_id).count() > 0:
            flash("A música está em playlists! Não pode ser deletada.", "warning")
            return redirect(url_for("crud_musicas"))

        db.session.delete(musica)
        db.session.commit()
        flash("Música removida!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao deletar música: {str(e)}", "danger")

    return redirect(url_for("crud_musicas"))


@app.route("/admin/musicas/<int:musica_id>")
@login_required
@admin_required
def get_musica(musica_id):
    musica = Musicas.query.get_or_404(musica_id)
    return jsonify({
        "id": musica.id,
        "titulo": musica.titulo,
        "artista_nome": musica.artista.nome if musica.artista else "",
        "genero_tipo": musica.genero.tipo if musica.genero else "",
        "album_titulo": musica.album.titulo if musica.album else ""
    })


#Users - Crud
@app.route("/admin/usuarios")
@login_required
@admin_required
def crud_usuarios():
    usuarios = Usuarios.query.all()
    return render_template("crud_usuarios.html", usuarios=usuarios)


@app.route("/admin/usuarios/adicionar", methods=["POST"])
@login_required
@admin_required
def adicionar_usuario():
    try:
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        tipo_usuario = request.form.get("tipo_usuario") or "usuario"

        if not nome or not email or not senha:
            flash("Preencha todos os campos obrigatórios!", "danger")
            return redirect(url_for("crud_usuarios"))

        if Usuarios.query.filter_by(email=email).first():
            flash("Este email já está cadastrado!", "danger")
            return redirect(url_for("crud_usuarios"))

        novo = Usuarios(
            nome=nome,
            email=email,
            tipo_usuario=tipo_usuario
        )
        novo.set_password(senha)

        db.session.add(novo)
        db.session.commit()
        flash("Usuário adicionado com sucesso!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao adicionar usuário: {str(e)}", "danger")

    return redirect(url_for("crud_usuarios"))


@app.route("/admin/usuarios/editar/<int:usuario_id>", methods=["POST"])
@login_required
@admin_required
def editar_usuario(usuario_id):
    try:
        usuario = Usuarios.query.get_or_404(usuario_id)
        usuario.nome = request.form.get("nome")
        usuario.email = request.form.get("email")
        usuario.tipo_usuario = request.form.get("tipo_usuario") or usuario.tipo_usuario

        senha = request.form.get("senha")
        if senha and senha.strip() != "":
            usuario.set_password(senha)

        db.session.commit()
        flash("Usuário atualizado com sucesso!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao atualizar usuário: {str(e)}", "danger")

    return redirect(url_for("crud_usuarios"))


@app.route("/admin/usuarios/deletar/<int:usuario_id>")
@login_required
@admin_required
def deletar_usuario(usuario_id):
    try:
        usuario = Usuarios.query.get_or_404(usuario_id)
        db.session.delete(usuario)
        db.session.commit()
        flash("Usuário foi deletado!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao deletar usuário: {str(e)}", "danger")

    return redirect(url_for("crud_usuarios"))


@app.route("/admin/usuarios/<int:usuario_id>")
@login_required
@admin_required
def get_usuario(usuario_id):
    usuario = Usuarios.query.get_or_404(usuario_id)
    return jsonify({
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "tipo_usuario": usuario.tipo_usuario,
        "payment_plan": usuario.payment_plan,
        "foto_perfil": usuario.foto_perfil
    })


#Perfil do User
@app.route("/profile", methods=["GET"])
@login_required
def profile():
    return render_template("profile.html", usuario=current_user)


@app.route("/profile/update", methods=["POST"])
@login_required
def profile_update():
    try:
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        foto = request.form.get("foto_base64")

        current_user.nome = nome
        current_user.email = email

        if foto and foto != "":
            current_user.foto_perfil = foto

        if senha and senha.strip() != "":
            current_user.set_password(senha)

        db.session.commit()
        return jsonify({"status": "ok"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)})

# Adicionar aos favoritos
@app.route("/favoritar/<int:musica_id>", methods=["POST"])
@login_required
def favoritar(musica_id):
    # verifica se a música existe
    musica = Musicas.query.get_or_404(musica_id)

    existe = Favoritos.query.filter_by(usuario_id=current_user.id, musica_id=musica_id).first()
    if existe:
        flash("Você já curtiu essa música!", "info")
        return redirect(request.referrer or url_for("index"))

    novo = Favoritos(usuario_id=current_user.id, musica_id=musica_id)
    db.session.add(novo)
    db.session.commit()
    flash("Música adicionada aos favoritos!", "success")
    return redirect(request.referrer or url_for("index"))


# Remover dos favoritos
@app.route("/remover_favorito/<int:musica_id>", methods=["POST"])
@login_required
def remover_favorito(musica_id):
    fav = Favoritos.query.filter_by(usuario_id=current_user.id, musica_id=musica_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        flash("Música removida dos favoritos!", "success")
    else:
        flash("Favorito não encontrado.", "warning")
    return redirect(request.referrer or url_for("liked"))


#Favoritos
@app.route("/liked")
@login_required
def liked():
    favoritos = current_user.favoritos

    musicas = [f.musica for f in favoritos]

    return render_template("liked.html", musicas=musicas)




@app.route("/playlist")
@login_required
def playlist():
    playlists = Playlist.query.filter_by(usuario_id=current_user.id).all()
    return render_template("playlists.html", playlists=playlists)


@app.route("/playlist/criar", methods=["POST"])
@login_required
def criar_playlist():
    nome = request.form.get("nome")
    descricao = request.form.get("descricao")

    if not nome:
        flash("O nome é obrigatório.", "danger")
        return redirect(url_for("playlist"))

    nova = Playlist(nome=nome, descricao=descricao, usuario_id=current_user.id)
    db.session.add(nova)
    db.session.commit()

    flash("Playlist criada.", "success")
    return redirect(url_for("playlist"))


@app.route("/playlist/editar/<int:playlist_id>", methods=["POST"])
@login_required
def editar_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)

    if playlist.usuario_id != current_user.id:
        flash("Acesso negado.", "danger")
        return redirect(url_for("playlist"))

    playlist.nome = request.form.get("nome")
    playlist.descricao = request.form.get("descricao")
    db.session.commit()

    flash("Playlist atualizada.", "success")
    return redirect(url_for("playlist"))


@app.route("/playlist/deletar/<int:playlist_id>", methods=["POST"])
@login_required
def deletar_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)

    if playlist.usuario_id != current_user.id:
        flash("Acesso negado.", "danger")
        return redirect(url_for("playlist"))

    db.session.delete(playlist)
    db.session.commit()

    flash("Playlist deletada.", "success")
    return redirect(url_for("playlist"))


@app.route("/playlist/<int:playlist_id>")
@login_required
def ver_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)

    if playlist.usuario_id != current_user.id:
        flash("Acesso negado.", "danger")
        return redirect(url_for("playlist"))

    musicas_playlist = playlist.musicas
    musicas = Musicas.query.all()
    

    return render_template(
        "playlist_detalhes.html",
        playlist=playlist,
        musicas_playlist=musicas_playlist,
        musicas=musicas
    )


@app.route("/playlist/<int:playlist_id>/add/<int:musica_id>")
@login_required
def playlist_musica(playlist_id, musica_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    musica = Musicas.query.get_or_404(musica_id)

    if musica not in playlist.musicas:
        playlist.musicas.append(musica)
        db.session.commit()
        flash("Música adicionada.", "success")

    return redirect(url_for("ver_playlist", playlist_id=playlist_id))


@app.route("/playlist/<int:playlist_id>/remove/<int:musica_id>")
@login_required
def remover_musica(playlist_id, musica_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    musica = Musicas.query.get_or_404(musica_id)

    if musica in playlist.musicas:
        playlist.musicas.remove(musica)
        db.session.commit()
        flash("Música removida.", "success")

    return redirect(url_for("ver_playlist", playlist_id=playlist_id))


@app.route("/home")
def home():
    return render_template("home.html")


# EXECUÇÃO
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)