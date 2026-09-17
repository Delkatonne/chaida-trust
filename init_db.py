"""
Initialise la base de données, crée le premier admin et les activités de base.
Usage : python init_db.py
"""
from app import create_app, db
from app.models import Admin, Activity

app = create_app()

ACTIVITES_DEFAUT = [
    {
        "nom": "Phytothérapie & Cosmétologie",
        "slug": "phytotherapie-cosmetologie",
        "description_courte": "Soins naturels à base de plantes et produits cosmétiques.",
        "ordre": 1,
        "propose_formation": True,
    },
    {
        "nom": "Création de mode",
        "slug": "creation-de-mode",
        "description_courte": "Design et confection de vêtements sur-mesure.",
        "ordre": 2,
        "propose_formation": True,
    },
    {
        "nom": "Esthétique",
        "slug": "esthetique",
        "description_courte": "Soins esthétiques et bien-être.",
        "ordre": 3,
        "propose_formation": True,
    },
    {
        "nom": "Marketing digital",
        "slug": "marketing-digital",
        "description_courte": "Stratégie et gestion de présence en ligne.",
        "ordre": 4,
        "propose_formation": True,
    },
    {
        "nom": "Formation",
        "slug": "formation",
        "description_courte": "Formations professionnalisantes dans nos domaines d'expertise.",
        "ordre": 5,
        "propose_formation": False,
    },
]

with app.app_context():
    db.create_all()

    if not Admin.query.filter_by(email="admin@chaidatrust.com").first():
        admin = Admin(nom="Administrateur", email="admin@chaidatrust.com", role="admin")
        admin.set_password("changez-ce-mot-de-passe")
        db.session.add(admin)
        print("✔ Compte admin créé : admin@chaidatrust.com / changez-ce-mot-de-passe")
        print("  -> Changez ce mot de passe immédiatement après la première connexion.")
    else:
        print("✔ Compte admin déjà existant.")

    if not Activity.query.first():
        for data in ACTIVITES_DEFAUT:
            db.session.add(Activity(visible=True, **data))
        print(f"✔ {len(ACTIVITES_DEFAUT)} activités créées (à compléter avec les vraies descriptions/images).")
    else:
        print("✔ Activités déjà existantes.")

    db.session.commit()
