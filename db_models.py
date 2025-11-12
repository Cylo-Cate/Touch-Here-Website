from database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Usuarios(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    tipo_usuario = db.Column(db.String(8), nullable=False)
    payment_plan = db.Column(db.String(255, nullable=False))

     # Relacionamentos
    playlists = db.relationship('Playlist', backref='usuario', lazy=True)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Usuarios {self.nome}>'

class Artistas(db.Model):
    __tablename__ = 'artistas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    nacionalidade = db.Column(db.String(50))
    
    # Relacionamentos
    musicas = db.relationship('Musicas', backref='artista', lazy=True)
    albuns = db.relationship('Albuns', backref='artista', lazy=True)
    
    def __repr__(self):
        return f'<Artistas {self.nome}>'

class Genero(db.Model):
    __tablename__ = 'generos'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False, unique=True)
    
    # Relacionamentos
    musicas = db.relationship('Musicas', backref='genero', lazy=True)
    
    def __repr__(self):
        return f'<Genero {self.tipo}>'

class Albuns(db.Model):
    __tablename__ = 'albuns'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    ano_lancamento = db.Column(db.Integer)
    artista_id = db.Column(db.Integer, db.ForeignKey('artistas.id'), nullable=False)
    
    # Relacionamentos
    musicas = db.relationship('Musicas', backref='album', lazy=True)
    
    def __repr__(self):
        return f'<Albuns {self.titulo}>'

class Musicas(db.Model):
    __tablename__ = 'musicas'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    duracao = db.Column(db.Integer)  # em segundos
    artista_id = db.Column(db.Integer, db.ForeignKey('artistas.id'), nullable=False)
    genero_id = db.Column(db.Integer, db.ForeignKey('generos.id'), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('albuns.id'))
    
    # Relacionamentos muitos-para-muitos com Playlist (tabela associativa)
    playlists = db.relationship('Playlist', secondary='playlist_musicas', back_populates='musicas')
    
    def __repr__(self):
        return f'<Musicas {self.titulo}>'

class Playlist(db.Model):
    __tablename__ = 'playlists'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data_criacao = db.Column()
    
    # Relacionamentos muitos-para-muitos com Musicas (tabela associativa)
    musicas = db.relationship('Musicas', secondary='playlist_musicas', back_populates='playlists')
    
    def __repr__(self):
        return f'<Playlist {self.nome}>'

# Tabela associativa para relação muitos-para-muitos entre Playlist e Musicas
class PlaylistMusicas(db.Model):
    __tablename__ = 'playlist_musicas'
    
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'), primary_key=True)
    musica_id = db.Column(db.Integer, db.ForeignKey('musicas.id'), primary_key=True)
    data_adicao = db.Column()
    
    def __repr__(self):
        return f'<PlaylistMusicas {self.playlist_id}-{self.musica_id}>'

