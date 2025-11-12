from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()#Instancia o SQL_Alchemy

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()#Cria as Tabelas