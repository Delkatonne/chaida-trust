from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class Admin(UserMixin, db.Model):
    """Compte du back-office (le client / le gérant)."""

    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="admin")
    actif = db.Column(db.Boolean, default=True)
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Activity(db.Model):
    """Un domaine d'activité de Chaïda Trust (a sa propre page publique)."""

    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(140), unique=True, nullable=False)
    icone = db.Column(db.String(50))
    description_courte = db.Column(db.String(300))
    description_longue = db.Column(db.Text)
    image = db.Column(db.String(255))
    ordre = db.Column(db.Integer, default=0)
    visible = db.Column(db.Boolean, default=True)
    propose_formation = db.Column(db.Boolean, default=False)

    produits = db.relationship("Product", backref="activite", lazy="dynamic")
    reservations = db.relationship(
        "BookingRequest", backref="activite", lazy="dynamic",
        foreign_keys="BookingRequest.activite_id"
    )


class Supplier(db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    contact = db.Column(db.String(150))
    telephone = db.Column(db.String(30))
    email = db.Column(db.String(120))
    adresse = db.Column(db.String(255))
    notes = db.Column(db.Text)
    actif = db.Column(db.Boolean, default=True)
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)

    produits = db.relationship("Product", backref="fournisseur", lazy="dynamic")


class Product(db.Model):
    """Produit éventuellement présenté sur une page d'activité (catalogue vitrine)."""

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(180), unique=True, nullable=False)
    description = db.Column(db.Text)
    prix = db.Column(db.Numeric(12, 2), nullable=True)
    unite = db.Column(db.String(30), default="unité")
    stock = db.Column(db.Integer, default=0)
    image = db.Column(db.String(255))
    disponible = db.Column(db.Boolean, default=True)
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)

    activite_id = db.Column(db.Integer, db.ForeignKey("activities.id"), nullable=False)
    fournisseur_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"), nullable=True)


class Client(db.Model):
    """Client / prospect de Chaïda Trust."""

    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    telephone = db.Column(db.String(40))
    email = db.Column(db.String(120))
    notes = db.Column(db.Text)
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)

    reservations = db.relationship("BookingRequest", backref="client", lazy="dynamic")
    inscriptions = db.relationship("TrainingRegistration", backref="client", lazy="dynamic")


class BookingRequest(db.Model):
    """Demande de réservation de programme / rendez-vous, liée à une activité."""

    __tablename__ = "booking_requests"

    STATUTS = ["nouvelle", "contactee", "confirmee", "annulee"]

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(30), unique=True, nullable=False)

    activite_id = db.Column(db.Integer, db.ForeignKey("activities.id"), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)

    indicatif_pays = db.Column(db.String(10), nullable=False, default="+229")
    telephone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120))

    programme_souhaite = db.Column(db.String(200))
    date_souhaitee = db.Column(db.String(60))
    message = db.Column(db.Text)

    statut = db.Column(db.String(20), default="nouvelle")
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)


class TrainingRegistration(db.Model):
    """Inscription à une formation dans un des domaines."""

    __tablename__ = "training_registrations"

    STATUTS = ["nouvelle", "contactee", "confirmee", "annulee"]

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(30), unique=True, nullable=False)

    activite_id = db.Column(db.Integer, db.ForeignKey("activities.id"), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)

    indicatif_pays = db.Column(db.String(10), nullable=False, default="+229")
    telephone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120))

    niveau = db.Column(db.String(60))
    motivation = db.Column(db.Text)

    statut = db.Column(db.String(20), default="nouvelle")
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)

    domaine = db.relationship("Activity", foreign_keys=[activite_id])


class ContactMessage(db.Model):
    """Message envoyé depuis la page contact."""

    __tablename__ = "contact_messages"

    STATUTS = ["nouveau", "traite"]

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    indicatif_pays = db.Column(db.String(10), default="+229")
    telephone = db.Column(db.String(30))
    motif = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)

    statut = db.Column(db.String(20), default="nouveau")
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)
