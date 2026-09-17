from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import Admin

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/admin/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        admin = Admin.query.filter_by(email=email).first()

        if admin and admin.actif and admin.check_password(password):
            login_user(admin, remember=True)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("admin.dashboard"))

        flash("Email ou mot de passe incorrect.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/admin/logout")
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for("auth.login"))
