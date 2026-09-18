import uuid
from flask import Blueprint, render_template, redirect, url_for, request, flash
from app import db
from app.models import Activity, Product, Client, BookingRequest, TrainingRegistration, ContactMessage

public_bp = Blueprint("public", __name__)

INDICATIFS_PAYS = [
    ("+229", "Bénin (+229)"),
    ("+225", "Côte d'Ivoire (+225)"),
    ("+228", "Togo (+228)"),
    ("+233", "Ghana (+233)"),
    ("+234", "Nigeria (+234)"),
    ("+221", "Sénégal (+221)"),
    ("+226", "Burkina Faso (+226)"),
    ("+223", "Mali (+223)"),
    ("+227", "Niger (+227)"),
    ("+237", "Cameroun (+237)"),
    ("+33", "France (+33)"),
    ("+1", "États-Unis / Canada (+1)"),
]

# Palette par domaine d'activité — chaque page /service/<slug> reprend ces
# couleurs pour donner une identité propre à chaque activité de Chaïda Trust.
ACTIVITY_THEMES = {
    "phytotherapie-cosmetologie": {  # vert / blanc — esprit médical, naturel
        "section_bg": "bg-green-50",
        "heading": "text-green-800",
        "accent_bg": "bg-green-600 hover:bg-green-700",
        "accent_text": "text-green-700",
        "border": "border-green-200",
        "badge": "bg-green-100 text-green-800",
        "ring": "ring-green-100",
    },
    "esthetique": {  # rose / blanc / doré
        "section_bg": "bg-pink-50",
        "heading": "text-pink-700",
        "accent_bg": "bg-gradient-to-r from-pink-500 to-amber-400 hover:from-pink-600 hover:to-amber-500",
        "accent_text": "text-pink-600",
        "border": "border-pink-200",
        "badge": "bg-pink-100 text-pink-700",
        "ring": "ring-pink-100",
    },
    "marketing-digital": {  # bleu / orange / vert
        "section_bg": "bg-blue-50",
        "heading": "text-blue-800",
        "accent_bg": "bg-orange-500 hover:bg-orange-600",
        "accent_text": "text-blue-700",
        "border": "border-blue-200",
        "badge": "bg-blue-100 text-blue-800",
        "ring": "ring-blue-100",
    },
}

DEFAULT_THEME = {  # mode, formation, et tout nouveau domaine ajouté sans thème dédié
    "section_bg": "bg-ivory",
    "heading": "text-forest-800",
    "accent_bg": "bg-plum-600 hover:bg-plum-700",
    "accent_text": "text-plum-600",
    "border": "border-gold-100",
    "badge": "bg-ivory text-forest-800",
    "ring": "ring-gold-100",
}


def get_activity_theme(slug):
    return ACTIVITY_THEMES.get(slug, DEFAULT_THEME)


def _get_or_create_client(nom, telephone, email):
    client = None
    if email:
        client = Client.query.filter_by(email=email).first()
    if not client:
        client = Client(nom=nom, telephone=telephone, email=email)
        db.session.add(client)
        db.session.flush()
    else:
        client.nom = nom or client.nom
        client.telephone = telephone or client.telephone
    return client


@public_bp.route("/")
def home():
    activites = Activity.query.filter_by(visible=True).order_by(Activity.ordre).all()
    return render_template("public/home.html", activites=activites)


@public_bp.route("/services")
def services():
    activites = Activity.query.filter_by(visible=True).order_by(Activity.ordre).all()
    themes = {a.slug: get_activity_theme(a.slug) for a in activites}
    return render_template("public/services.html", activites=activites, themes=themes)


@public_bp.route("/service/<slug>", methods=["GET", "POST"])
def activity_detail(slug):
    activite = Activity.query.filter_by(slug=slug, visible=True).first_or_404()
    produits = activite.produits.filter_by(disponible=True).all()
    theme = get_activity_theme(slug)

    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        telephone = request.form.get("telephone", "").strip()
        indicatif = request.form.get("indicatif_pays", "+229")
        email = request.form.get("email", "").strip()
        programme = request.form.get("programme_souhaite", "").strip()
        date_souhaitee = request.form.get("date_souhaitee", "").strip()
        message = request.form.get("message", "").strip()

        if not nom or not telephone:
            flash("Le nom et le téléphone sont obligatoires.", "danger")
            return render_template(
                "public/activity.html", activite=activite, produits=produits,
                indicatifs=INDICATIFS_PAYS, theme=theme,
            )

        client = _get_or_create_client(nom, telephone, email)

        reservation = BookingRequest(
            reference=f"RDV-{uuid.uuid4().hex[:8].upper()}",
            activite_id=activite.id,
            client_id=client.id,
            indicatif_pays=indicatif,
            telephone=telephone,
            email=email,
            programme_souhaite=programme,
            date_souhaitee=date_souhaitee,
            message=message,
        )
        db.session.add(reservation)
        db.session.commit()

        return redirect(url_for("public.booking_confirmation", reference=reservation.reference))

    return render_template(
        "public/activity.html", activite=activite, produits=produits,
        indicatifs=INDICATIFS_PAYS, theme=theme,
    )


@public_bp.route("/reservation/confirmation/<reference>")
def booking_confirmation(reference):
    reservation = BookingRequest.query.filter_by(reference=reference).first_or_404()
    return render_template("public/booking_confirmation.html", reservation=reservation)


@public_bp.route("/formations", methods=["GET", "POST"])
def formations():
    domaines = Activity.query.filter_by(visible=True, propose_formation=True).order_by(Activity.ordre).all()

    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        telephone = request.form.get("telephone", "").strip()
        indicatif = request.form.get("indicatif_pays", "+229")
        email = request.form.get("email", "").strip()
        activite_id = request.form.get("activite_id")
        niveau = request.form.get("niveau", "").strip()
        motivation = request.form.get("motivation", "").strip()

        if not nom or not telephone or not activite_id:
            flash("Le nom, le téléphone et le domaine de formation sont obligatoires.", "danger")
            return render_template("public/formations.html", domaines=domaines, indicatifs=INDICATIFS_PAYS)

        client = _get_or_create_client(nom, telephone, email)

        inscription = TrainingRegistration(
            reference=f"FORM-{uuid.uuid4().hex[:8].upper()}",
            activite_id=int(activite_id),
            client_id=client.id,
            indicatif_pays=indicatif,
            telephone=telephone,
            email=email,
            niveau=niveau,
            motivation=motivation,
        )
        db.session.add(inscription)
        db.session.commit()

        return redirect(url_for("public.training_confirmation", reference=inscription.reference))

    return render_template("public/formations.html", domaines=domaines, indicatifs=INDICATIFS_PAYS)


@public_bp.route("/formations/confirmation/<reference>")
def training_confirmation(reference):
    inscription = TrainingRegistration.query.filter_by(reference=reference).first_or_404()
    return render_template("public/training_confirmation.html", inscription=inscription)


@public_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        email = request.form.get("email", "").strip()
        indicatif = request.form.get("indicatif_pays", "+229")
        telephone = request.form.get("telephone", "").strip()
        motif = request.form.get("motif", "").strip()
        message = request.form.get("message", "").strip()

        if not nom or not email or not motif or not message:
            flash("Nom, email, motif et message sont obligatoires.", "danger")
            return render_template("public/contact.html", indicatifs=INDICATIFS_PAYS)

        contact_msg = ContactMessage(
            nom=nom, email=email, indicatif_pays=indicatif, telephone=telephone,
            motif=motif, message=message,
        )
        db.session.add(contact_msg)
        db.session.commit()

        flash("Votre message a bien été envoyé. Nous vous répondrons rapidement.", "success")
        return redirect(url_for("public.contact"))

    return render_template("public/contact.html", indicatifs=INDICATIFS_PAYS)