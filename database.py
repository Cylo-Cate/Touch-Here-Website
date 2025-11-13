from db_models import db
db.init_app(app)

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()#Cria as Tabelas
        print("Todas as Tabelas foram Criadas")