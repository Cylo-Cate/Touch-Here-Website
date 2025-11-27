from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()  # Instância do SQLAlchemy

class Usuarios(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    tipo_usuario = db.Column(db.String(20), nullable=False, default='usuario')
    payment_plan = db.Column(db.String(50), nullable=False, default='free')
    foto_perfil = db.Column(db.Text, nullable=True)

    # Relacionamentos
    playlists = db.relationship(
        'Playlist',
        backref='usuario',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def set_password(self, password: str) -> None:
        """Gera e salva o hash da senha."""
        self.senha = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifica se a senha fornecida confere com o hash salvo."""
        if not self.senha:
            return False
        return check_password_hash(self.senha, password)

    @property
    def is_admin(self) -> bool:
        return (self.tipo_usuario or '').lower() == 'admin'

    def __repr__(self):
        return f'<Usuarios {self.nome}>'

class Artistas(db.Model):
    __tablename__ = 'artistas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

    # Relacionamentos
    musicas = db.relationship('Musicas', backref='artista', lazy=True, cascade='all, delete-orphan')
    albuns = db.relationship('Albuns', backref='artista', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Artistas {self.nome}>'

class Genero(db.Model):
    __tablename__ = 'generos'

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False, unique=True)

    # Relacionamentos
    musicas = db.relationship('Musicas', backref='genero', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Genero {self.tipo}>'

class Albuns(db.Model):
    __tablename__ = 'albuns'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    artista_id = db.Column(db.Integer, db.ForeignKey('artistas.id'), nullable=False)

    # Relacionamentos
    musicas = db.relationship('Musicas', backref='album', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Albuns {self.titulo}>'

class Musicas(db.Model):
    __tablename__ = 'musicas'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    artista_id = db.Column(db.Integer, db.ForeignKey('artistas.id'), nullable=False)
    genero_id = db.Column(db.Integer, db.ForeignKey('generos.id'), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('albuns.id'))
    caminho_pasta = db.Column(db.String(200), nullable=False)

    # Relacionamentos muitos-para-muitos com Playlist (tabela associativa)
    playlists = db.relationship(
        'Playlist',
        secondary='playlist_musicas',
        back_populates='musicas'
    )

    def __repr__(self):
        return f'<Musicas {self.titulo}>'

class Playlist(db.Model):
    __tablename__ = 'playlists'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    # Relacionamentos muitos-para-muitos com Musicas (tabela associativa)
    musicas = db.relationship(
        'Musicas',
        secondary='playlist_musicas',
        back_populates='playlists'
    )

    def __repr__(self):
        return f'<Playlist {self.nome}>'

# Tabela associativa para relação muitos-para-muitos entre Playlist e Musicas
class PlaylistMusicas(db.Model):
    __tablename__ = 'playlist_musicas'

    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'), primary_key=True)
    musica_id = db.Column(db.Integer, db.ForeignKey('musicas.id'), primary_key=True)

    def __repr__(self):
        return f'<PlaylistMusicas {self.playlist_id}-{self.musica_id}>'

class Favoritos(db.Model):
    __tablename__ = "favoritos"

    id = db.Column(db.Integer, primary_key=True)

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    musica_id = db.Column(db.Integer, db.ForeignKey("musicas.id"), nullable=False)

    usuario = db.relationship("Usuarios", backref="favoritos", lazy=True)
    musica = db.relationship("Musicas", lazy=True)

    def __repr__(self):
        return f'<Favorito user={self.usuario_id} musica={self.musica_id}>'

