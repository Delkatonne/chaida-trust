import os
import re
import unicodedata
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required
from app import db
from app.models import (
    Activity, Product, Supplier, Client,
    BookingRequest, TrainingRegistration, ContactMessage,
)

admin_bp = Blueprint("admin", __name__)


def slugify(texte):
    texte = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode("ascii")
    texte = re.sub(r"[^\w\s-]", "", texte).strip().lower()
    return re.sub(r"[\s_-]+", "-", texte)


def save_image(fichier):
    if not fichier or not fichier.filename:
        return None
    nom = secure_filename(fichier.filename)
    chemin = os.path.join(current_app.config["UPLOAD_FOLDER"], nom)
    fichier.save(chemin)
    return f"uploads/{nom}"


# ---------- Dashboard ----------

@admin_bp.route("/")
@login_required
def dashboard():
    stats = {
        "reservations_nouvelles": BookingRequest.query.filter_by(statut="nouvelle").count(),
        "reservations_total": BookingRequest.query.count(),
        "inscriptions_nouvelles": TrainingRegistration.query.filter_by(statut="nouvelle").count(),
        "messages_nouveaux": ContactMessage.query.filter_by(statut="nouveau").count(),
        "produits_total": Product.query.count(),
        "clients_total": Client.query.count(),
        "fournisseurs_total": Supplier.query.count(),
    }
    dernieres_reservations = BookingRequest.query.order_by(BookingRequest.cree_le.desc()).limit(6).all()
    dernieres_inscriptions = TrainingRegistration.query.order_by(TrainingRegistration.cree_le.desc()).limit(6).all()
    derniers_messages = ContactMessage.query.order_by(ContactMessage.cree_le.desc()).limit(6).all()
    return render_template(
        "admin/dashboard.html", stats=stats,
        reservations=dernieres_reservations, inscriptions=dernieres_inscriptions, messages=derniers_messages,
    )


# ---------- Activités ----------

@admin_bp.route("/activites")
@login_required
def activities_list():
    activites = Activity.query.order_by(Activity.ordre).all()
    return render_template("admin/activities_list.html", activites=activites)


@admin_bp.route("/activites/nouvelle", methods=["GET", "POST"])
@login_required
def activity_new():
    if request.method == "POST":
        nom = request.form["nom"].strip()
        activite = Activity(
            nom=nom,
            slug=slugify(nom),
            description_courte=request.form.get("description_courte", "").strip(),
            description_longue=request.form.get("description_longue", "").strip(),
            ordre=int(request.form.get("ordre", 0)),
            visible="visible" in request.form,
            propose_formation="propose_formation" in request.form,
            image=save_image(request.files.get("image")),
        )
        db.session.add(activite)
        db.session.commit()
        flash("Activité créée.", "success")
        return redirect(url_for("admin.activities_list"))
    return render_template("admin/activity_form.html", activite=None)


@admin_bp.route("/activites/<int:id>/modifier", methods=["GET", "POST"])
@login_required
def activity_edit(id):
    activite = Activity.query.get_or_404(id)
    if request.method == "POST":
        activite.nom = request.form["nom"].strip()
        activite.description_courte = request.form.get("description_courte", "").strip()
        activite.description_longue = request.form.get("description_longue", "").strip()
        activite.ordre = int(request.form.get("ordre", 0))
        activite.visible = "visible" in request.form
        activite.propose_formation = "propose_formation" in request.form
        nouvelle_image = save_image(request.files.get("image"))
        if nouvelle_image:
            activite.image = nouvelle_image
        db.session.commit()
        flash("Activité mise à jour.", "success")
        return redirect(url_for("admin.activities_list"))
    return render_template("admin/activity_form.html", activite=activite)


@admin_bp.route("/activites/<int:id>/supprimer", methods=["POST"])
@login_required
def activity_delete(id):
    activite = Activity.query.get_or_404(id)
    db.session.delete(activite)
    db.session.commit()
    flash("Activité supprimée.", "info")
    return redirect(url_for("admin.activities_list"))


# ---------- Produits ----------

@admin_bp.route("/produits")
@login_required
def products_list():
    produits = Product.query.order_by(Product.cree_le.desc()).all()
    return render_template("admin/products_list.html", produits=produits)


@admin_bp.route("/produits/nouveau", methods=["GET", "POST"])
@login_required
def product_new():
    activites = Activity.query.order_by(Activity.ordre).all()
    fournisseurs = Supplier.query.filter_by(actif=True).order_by(Supplier.nom).all()

    if request.method == "POST":
        nom = request.form["nom"].strip()
        prix = request.form.get("prix", "").strip()
        produit = Product(
            nom=nom,
            slug=slugify(nom) + f"-{Product.query.count() + 1}",
            description=request.form.get("description", "").strip(),
            prix=prix or None,
            unite=request.form.get("unite", "unité"),
            stock=int(request.form.get("stock", 0)),
            disponible="disponible" in request.form,
            activite_id=int(request.form["activite_id"]),
            fournisseur_id=request.form.get("fournisseur_id") or None,
            image=save_image(request.files.get("image")),
        )
        db.session.add(produit)
        db.session.commit()
        flash("Produit créé.", "success")
        return redirect(url_for("admin.products_list"))

    return render_template("admin/product_form.html", produit=None, activites=activites, fournisseurs=fournisseurs)


@admin_bp.route("/produits/<int:id>/modifier", methods=["GET", "POST"])
@login_required
def product_edit(id):
    produit = Product.query.get_or_404(id)
    activites = Activity.query.order_by(Activity.ordre).all()
    fournisseurs = Supplier.query.filter_by(actif=True).order_by(Supplier.nom).all()

    if request.method == "POST":
        produit.nom = request.form["nom"].strip()
        produit.description = request.form.get("description", "").strip()
        prix = request.form.get("prix", "").strip()
        produit.prix = prix or None
        produit.unite = request.form.get("unite", "unité")
        produit.stock = int(request.form.get("stock", 0))
        produit.disponible = "disponible" in request.form
        produit.activite_id = int(request.form["activite_id"])
        produit.fournisseur_id = request.form.get("fournisseur_id") or None
        nouvelle_image = save_image(request.files.get("image"))
        if nouvelle_image:
            produit.image = nouvelle_image
        db.session.commit()
        flash("Produit mis à jour.", "success")
        return redirect(url_for("admin.products_list"))

    return render_template("admin/product_form.html", produit=produit, activites=activites, fournisseurs=fournisseurs)


@admin_bp.route("/produits/<int:id>/supprimer", methods=["POST"])
@login_required
def product_delete(id):
    produit = Product.query.get_or_404(id)
    db.session.delete(produit)
    db.session.commit()
    flash("Produit supprimé.", "info")
    return redirect(url_for("admin.products_list"))


# ---------- Fournisseurs ----------

@admin_bp.route("/fournisseurs")
@login_required
def suppliers_list():
    fournisseurs = Supplier.query.order_by(Supplier.nom).all()
    return render_template("admin/suppliers_list.html", fournisseurs=fournisseurs)


@admin_bp.route("/fournisseurs/nouveau", methods=["GET", "POST"])
@login_required
def supplier_new():
    if request.method == "POST":
        fournisseur = Supplier(
            nom=request.form["nom"].strip(),
            contact=request.form.get("contact", "").strip(),
            telephone=request.form.get("telephone", "").strip(),
            email=request.form.get("email", "").strip(),
            adresse=request.form.get("adresse", "").strip(),
            notes=request.form.get("notes", "").strip(),
            actif="actif" in request.form,
        )
        db.session.add(fournisseur)
        db.session.commit()
        flash("Fournisseur ajouté.", "success")
        return redirect(url_for("admin.suppliers_list"))
    return render_template("admin/supplier_form.html", fournisseur=None)


@admin_bp.route("/fournisseurs/<int:id>/modifier", methods=["GET", "POST"])
@login_required
def supplier_edit(id):
    fournisseur = Supplier.query.get_or_404(id)
    if request.method == "POST":
        fournisseur.nom = request.form["nom"].strip()
        fournisseur.contact = request.form.get("contact", "").strip()
        fournisseur.telephone = request.form.get("telephone", "").strip()
        fournisseur.email = request.form.get("email", "").strip()
        fournisseur.adresse = request.form.get("adresse", "").strip()
        fournisseur.notes = request.form.get("notes", "").strip()
        fournisseur.actif = "actif" in request.form
        db.session.commit()
        flash("Fournisseur mis à jour.", "success")
        return redirect(url_for("admin.suppliers_list"))
    return render_template("admin/supplier_form.html", fournisseur=fournisseur)


@admin_bp.route("/fournisseurs/<int:id>/supprimer", methods=["POST"])
@login_required
def supplier_delete(id):
    fournisseur = Supplier.query.get_or_404(id)
    db.session.delete(fournisseur)
    db.session.commit()
    flash("Fournisseur supprimé.", "info")
    return redirect(url_for("admin.suppliers_list"))


# ---------- Clients ----------

@admin_bp.route("/clients")
@login_required
def clients_list():
    clients = Client.query.order_by(Client.cree_le.desc()).all()
    return render_template("admin/clients_list.html", clients=clients)


@admin_bp.route("/clients/<int:id>")
@login_required
def client_detail(id):
    client = Client.query.get_or_404(id)
    reservations = client.reservations.order_by(BookingRequest.cree_le.desc()).all()
    inscriptions = client.inscriptions.order_by(TrainingRegistration.cree_le.desc()).all()
    return render_template("admin/client_detail.html", client=client, reservations=reservations, inscriptions=inscriptions)


# ---------- Réservations (RDV / programmes) ----------

@admin_bp.route("/reservations")
@login_required
def bookings_list():
    statut = request.args.get("statut")
    query = BookingRequest.query
    if statut:
        query = query.filter_by(statut=statut)
    reservations = query.order_by(BookingRequest.cree_le.desc()).all()
    return render_template("admin/bookings_list.html", reservations=reservations, statut_filtre=statut, statuts=BookingRequest.STATUTS)


@admin_bp.route("/reservations/<int:id>")
@login_required
def booking_detail(id):
    reservation = BookingRequest.query.get_or_404(id)
    return render_template("admin/booking_detail.html", reservation=reservation, statuts=BookingRequest.STATUTS)


@admin_bp.route("/reservations/<int:id>/statut", methods=["POST"])
@login_required
def booking_update_status(id):
    reservation = BookingRequest.query.get_or_404(id)
    nouveau_statut = request.form.get("statut")
    if nouveau_statut in BookingRequest.STATUTS:
        reservation.statut = nouveau_statut
        db.session.commit()
        flash("Statut mis à jour.", "success")
    return redirect(url_for("admin.booking_detail", id=id))


# ---------- Inscriptions formation ----------

@admin_bp.route("/formations-inscriptions")
@login_required
def trainings_list():
    statut = request.args.get("statut")
    query = TrainingRegistration.query
    if statut:
        query = query.filter_by(statut=statut)
    inscriptions = query.order_by(TrainingRegistration.cree_le.desc()).all()
    return render_template("admin/trainings_list.html", inscriptions=inscriptions, statut_filtre=statut, statuts=TrainingRegistration.STATUTS)


@admin_bp.route("/formations-inscriptions/<int:id>")
@login_required
def training_detail(id):
    inscription = TrainingRegistration.query.get_or_404(id)
    return render_template("admin/training_detail.html", inscription=inscription, statuts=TrainingRegistration.STATUTS)


@admin_bp.route("/formations-inscriptions/<int:id>/statut", methods=["POST"])
@login_required
def training_update_status(id):
    inscription = TrainingRegistration.query.get_or_404(id)
    nouveau_statut = request.form.get("statut")
    if nouveau_statut in TrainingRegistration.STATUTS:
        inscription.statut = nouveau_statut
        db.session.commit()
        flash("Statut mis à jour.", "success")
    return redirect(url_for("admin.training_detail", id=id))


# ---------- Messages de contact ----------

@admin_bp.route("/messages")
@login_required
def messages_list():
    messages = ContactMessage.query.order_by(ContactMessage.cree_le.desc()).all()
    return render_template("admin/messages_list.html", messages=messages)


@admin_bp.route("/messages/<int:id>/traite", methods=["POST"])
@login_required
def message_mark_treated(id):
    message = ContactMessage.query.get_or_404(id)
    message.statut = "traite"
    db.session.commit()
    return redirect(url_for("admin.messages_list"))
