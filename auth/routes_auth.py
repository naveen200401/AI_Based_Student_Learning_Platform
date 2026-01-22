from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists!")
            return redirect(url_for('auth_bp.register'))

        hashed = generate_password_hash(password)


        new_user = User(email=email, password=hashed)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! You can login now.")
        return redirect(url_for('auth_bp.login'))

    return render_template("register.html")

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash("Invalid Login!")
            return redirect(url_for('auth_bp.login'))

    return render_template("login.html")

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_bp.login'))
