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

    UPLOAD_FOLDER = os.path.join(basedir, "app", "static", "uploads")
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 Mo max par upload
