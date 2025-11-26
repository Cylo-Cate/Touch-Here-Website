from db_models import db, Usuarios

def init_db(app):
    """Inicializa o banco de dados e cria tabelas se não existirem."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        print("Tabelas verificadas e criadas (se necessário).")
        if not Usuarios.query.filter_by(tipo_usuario="admin").first():
            admin = Usuarios(
                nome="Admin",
                email="adm@touch4here",
                tipo_usuario="admin"
            )
            admin.set_password("1233")
            
            db.session.add(admin)
            db.session.commit()

            print("Admin criado com sucesso!")
