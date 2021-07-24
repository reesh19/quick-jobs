"""Authentication system"""

from flask import Blueprint, render_template, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from . import LM, DB

auth = Blueprint('auth', __name__)


@auth.route("/login", methods=["POST","GET"])
def login():
    """Checks if credentials match ones in DB"""
    if current_user.is_authenticated:
        return render_template("home.html")

    if request.method == "POST":
        email = request.values["email"]
        password = request.values["password"]

        credential = User.query.filter_by(email = email).first()

        if credential and (credential.password == password):
            login_user(credential)
            return render_template("home.html")

        flash("Incorrect email or password! Try again or register.")
        return render_template("login.html")

    return render_template("login.html")


@auth.route("/register", methods=["POST","GET"])
def register():
    """Checks if email is in use, otherwise adds user to DB"""
    if current_user.is_authenticated:
        return render_template("home.html")

    if request.method == "POST":
        user_email = request.values["email"]
        user_password = request.values["password"]
    
        credential = User.query.filter_by(email = user_email).first()

        if not credential:
            new_user = User(email=user_email, password=user_password)

            DB.session.add(new_user)
            DB.session.commit()

            login_user(new_user)

            return render_template("home.html")

        flash("Email already in use! Try again or login.")
        return render_template("register.html")

    return render_template("register.html")


@LM.user_loader
def load_user(user_id):
    """Checks if user is logged in"""
    if user_id:
        return User.query.get(user_id)
    return None


@LM.unauthorized_handler
def unauthorized():
    """Redirects unauthorized users"""
    flash("You must be logged in to view that page.")
    return render_template("login.html")
