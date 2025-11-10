from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DB = declarative_base()

playlist_musicas = Table(
    'playlist_musicas', DB.metadata,
    Column('playlist_id', Integer, ForeignKey('Playlists.id')),
    Column('musica_id', Integer, ForeignKey('Musicas.id'))
)

class Usuarios(DB):
    __tablename__ = 'Usuarios'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nickname = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    admin = Column(Boolean, default=False)

    playlists = relationship("Playlists", back_populates="usuario")


class Artistas(DB):
    __tablename__ = 'Artistas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    nacionalidade = Column(String(255), nullable=False)
    ano_estreia = Column(Integer, nullable=False)

    musicas = relationship("Musicas", back_populates="artista")


class Generos(DB):
    __tablename__ = 'Generos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), unique=True, nullable=False)
    descricao = Column(String(255), nullable=False)
    origem = Column(String(255), nullable=False)  

    musicas = relationship("Musicas", back_populates="genero")

class Albuns(DB):
    __tablename__ = 'Albuns'
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(255), nullable=False)
    ano_lancamento = Column(Integer, nullable=False)
    artista_id = Column(Integer, ForeignKey('Artistas.id'))

    musicas = relationship("Musicas", back_populates="album")


class Musicas(DB):
    __tablename__ = 'Musicas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(255), nullable=False)
    duracao = Column(String(10), nullable=False)
    artista_id = Column(Integer, ForeignKey('Artistas.id'))
    genero_id = Column(Integer, ForeignKey('Generos.id'))
    album_id = Column(Integer, ForeignKey('Albuns.id'))

    artista = relationship("Artistas", back_populates="musicas")
    genero = relationship("Generos", back_populates="musicas")
    album = relationship("Albuns", back_populates="musicas")

    playlists = relationship("Playlists", secondary=playlist_musicas, back_populates="musicas")


class Playlists(DB):
    __tablename__ = 'Playlists'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(String(255), nullable=False)
    usuario_id = Column(Integer, ForeignKey('Usuarios.id'), nullable=True)

    usuario = relationship("Usuarios", back_populates="playlists")
    musicas = relationship("Musicas", secondary=playlist_musicas, back_populates="playlists")



engine = create_engine("sqlite:///streaming.db")
DB.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

generos = [
    Generos(nome="Hip-Hop", descricao="Ritmos marcantes e rimas", origem="Estados Unidos"),
    Generos(nome="Trap", descricao="Derivado do rap com 808 forte", origem="Atlanta - EUA"),
    Generos(nome="Pop", descricao="Música popular de grande alcance", origem="Cultura global dos anos 80")
]
session.add_all(generos)
session.commit()

artistas = [
    Artistas(nome="Travis Scott", nacionalidade="Estados Unidos", ano_estreia=2013),
    Artistas(nome="Kendrick Lamar", nacionalidade="Estados Unidos", ano_estreia=2011),
    Artistas(nome="Drake", nacionalidade="Canadá", ano_estreia=2009),
    Artistas(nome="The Weeknd", nacionalidade="Canadá", ano_estreia=2011),
    Artistas(nome="21 Savage", nacionalidade="Reino Unido", ano_estreia=2014)
]
session.add_all(artistas)
session.commit()

g_hiphop = generos[0]
g_trap = generos[1]
g_pop = generos[2]

a1, a2, a3, a4, a5 = artistas

albuns = [
    Albuns(titulo="Rodeo", ano_lancamento=2015, artista_id=a1.id),
    Albuns(titulo="Astroworld", ano_lancamento=2018, artista_id=a1.id),

    Albuns(titulo="good kid, m.A.A.d city", ano_lancamento=2012, artista_id=a2.id),
    Albuns(titulo="DAMN.", ano_lancamento=2017, artista_id=a2.id),

    Albuns(titulo="Views", ano_lancamento=2016, artista_id=a3.id),
    Albuns(titulo="Scorpion", ano_lancamento=2018, artista_id=a3.id),

    Albuns(titulo="Starboy", ano_lancamento=2016, artista_id=a4.id),
    Albuns(titulo="After Hours", ano_lancamento=2020, artista_id=a4.id),

    Albuns(titulo="Issa Album", ano_lancamento=2017, artista_id=a5.id),
    Albuns(titulo="I Am > I Was", ano_lancamento=2018, artista_id=a5.id)
]
session.add_all(albuns)
session.commit()

musicas = [
    Musicas(titulo="90210", duracao="4:38", artista_id=a1.id, genero_id=g_trap.id, album_id=albuns[0].id),
    Musicas(titulo="Goosebumps", duracao="4:04", artista_id=a1.id, genero_id=g_trap.id, album_id=albuns[1].id),
    Musicas(titulo="SICKO MODE", duracao="5:12", artista_id=a1.id, genero_id=g_trap.id, album_id=albuns[1].id),

    Musicas(titulo="Money Trees", duracao="6:26", artista_id=a2.id, genero_id=g_hiphop.id, album_id=albuns[2].id),
    Musicas(titulo="HUMBLE.", duracao="2:57", artista_id=a2.id, genero_id=g_hiphop.id, album_id=albuns[3].id),
    Musicas(titulo="DNA.", duracao="3:06", artista_id=a2.id, genero_id=g_hiphop.id, album_id=albuns[3].id),

    Musicas(titulo="Hotline Bling", duracao="4:27", artista_id=a3.id, genero_id=g_pop.id, album_id=albuns[4].id),
    Musicas(titulo="God's Plan", duracao="3:19", artista_id=a3.id, genero_id=g_pop.id, album_id=albuns[5].id),
    Musicas(titulo="Nonstop", duracao="3:58", artista_id=a3.id, genero_id=g_hiphop.id, album_id=albuns[5].id),

    Musicas(titulo="Starboy", duracao="3:50", artista_id=a4.id, genero_id=g_pop.id, album_id=albuns[6].id),
    Musicas(titulo="Blinding Lights", duracao="3:20", artista_id=a4.id, genero_id=g_pop.id, album_id=albuns[7].id),
    Musicas(titulo="Save Your Tears", duracao="3:36", artista_id=a4.id, genero_id=g_pop.id, album_id=albuns[7].id),

    Musicas(titulo="Bank Account", duracao="3:40", artista_id=a5.id, genero_id=g_trap.id, album_id=albuns[8].id),
    Musicas(titulo="a lot", duracao="4:48", artista_id=a5.id, genero_id=g_trap.id, album_id=albuns[9].id),
    Musicas(titulo="No Heart", duracao="3:54", artista_id=a5.id, genero_id=g_trap.id, album_id=albuns[8].id),
]
session.add_all(musicas)
session.commit()

playlists = [
    Playlists(nome="Trap Vibes", descricao="Trap pesado e melódico", musicas=[musicas[0], musicas[2], musicas[12], musicas[13]]),
    Playlists(nome="Chill Night", descricao="Som leve para relaxar", musicas=[musicas[7], musicas[9], musicas[10], musicas[11]]),
    Playlists(nome="Rap Hits", descricao="Os melhores do rap moderno", musicas=[musicas[3], musicas[4], musicas[8], musicas[14]])
]
session.add_all(playlists)
session.commit()
