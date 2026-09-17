import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-moi-en-production")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'app.db')}"
    ).replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session admin
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # Kkiapay (à remplir dès que le compte marchand est créé)
    KKIAPAY_PUBLIC_KEY = os.environ.get("KKIAPAY_PUBLIC_KEY", "")
    KKIAPAY_PRIVATE_KEY = os.environ.get("KKIAPAY_PRIVATE_KEY", "")
    KKIAPAY_SECRET = os.environ.get("KKIAPAY_SECRET", "")
    KKIAPAY_SANDBOX = os.environ.get("KKIAPAY_SANDBOX", "true").lower() == "true"

    # Sur Vercel, le système de fichiers du projet est en lecture seule —
    # seul /tmp est inscriptible, et il n'est pas persistant ni servi publiquement.
    # Les images uploadées depuis l'admin ne survivront donc pas en production
    # tant qu'un stockage externe (Vercel Blob, Cloudinary...) n'est pas branché.
    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER",
        "/tmp/uploads" if os.environ.get("VERCEL") else os.path.join(basedir, "app", "static", "uploads"),
    )
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 Mo max par upload