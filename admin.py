from app import app
from db_models import db, Usuarios

with app.app_context():
    admin = Usuarios(
        nome="Admin",
        email="adm@touch4here",
        tipo_usuario="admin"
    )
    admin.set_password("1233")
    
    db.session.add(admin)
    db.session.commit()

    print("Admin criado com sucesso!")