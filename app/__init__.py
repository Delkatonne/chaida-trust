import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Merci de vous connecter pour accéder à cette page."
    login_manager.login_message_category = "warning"

    from app.models import Admin

    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    from app.routes.public import public_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    _auto_init_db(app)

    @app.context_processor
    def inject_globals():
        from app.models import Activity

        return {"activites_menu": Activity.query.order_by(Activity.ordre).all()}

    return app


def _auto_init_db(app):
    """
    Crée les tables et les données de départ (admin + activités) si elles
    n'existent pas encore. Permet de déployer sur Vercel sans avoir à lancer
    de script en local : tout se met en place tout seul au premier démarrage.
    Sans effet si les tables existent déjà (vérifie avant de rien insérer).
    """
    from app.models import Admin, Activity

    ACTIVITES_DEFAUT = [
        {"nom": "Phytothérapie & Cosmétologie", "slug": "phytotherapie-cosmetologie",
         "description_courte": "Soins naturels à base de plantes et produits cosmétiques.",
         "ordre": 1, "propose_formation": True},
        {"nom": "Création de mode", "slug": "creation-de-mode",
         "description_courte": "Design et confection de vêtements sur-mesure.",
         "ordre": 2, "propose_formation": True},
        {"nom": "Esthétique", "slug": "esthetique",
         "description_courte": "Soins esthétiques et bien-être.",
         "ordre": 3, "propose_formation": True},
        {"nom": "Marketing digital", "slug": "marketing-digital",
         "description_courte": "Stratégie et gestion de présence en ligne.",
         "ordre": 4, "propose_formation": True},
        {"nom": "Formation", "slug": "formation",
         "description_courte": "Formations professionnalisantes dans nos domaines d'expertise.",
         "ordre": 5, "propose_formation": False},
    ]

    try:
        with app.app_context():
            db.create_all()

            if not Admin.query.first():
                admin_email = os.environ.get("ADMIN_EMAIL", "admin@chaidatrust.com")
                admin_password = os.environ.get("ADMIN_PASSWORD", "changez-ce-mot-de-passe")
                admin = Admin(nom="Administrateur", email=admin_email, role="admin")
                admin.set_password(admin_password)
                db.session.add(admin)
                app.logger.info(f"Compte admin créé automatiquement : {admin_email}")

            if not Activity.query.first():
                for data in ACTIVITES_DEFAUT:
                    db.session.add(Activity(visible=True, **data))
                app.logger.info("Activités de départ créées automatiquement.")

            db.session.commit()
    except Exception as e:
        # On ne bloque jamais le démarrage de l'app si la DB n'est pas encore
        # joignable (ex: DATABASE_URL pas encore configuré) — les routes qui
        # en ont besoin échoueront simplement avec un message clair en log.
        app.logger.error(f"Initialisation automatique de la base impossible : {e}")