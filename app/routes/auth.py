from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from .. import db
from ..models import User
from ..utils import send_reset_email

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/inscription', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        nom    = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        email  = request.form.get('email', '').strip().lower()
        pwd    = request.form.get('password', '')
        pwd2   = request.form.get('password2', '')

        if not all([nom, prenom, email, pwd]):
            flash('Tous les champs sont obligatoires.', 'danger')
            return render_template('auth/register.html')
        if pwd != pwd2:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return render_template('auth/register.html')
        if len(pwd) < 8:
            flash('Le mot de passe doit contenir au moins 8 caractères.', 'danger')
            return render_template('auth/register.html')
        if User.query.filter_by(email=email).first():
            flash('Cette adresse email est déjà utilisée.', 'danger')
            return render_template('auth/register.html')

        user = User(nom=nom, prenom=prenom, email=email)
        user.set_password(pwd)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Bienvenue {user.full_name} ! Votre compte a été créé.', 'success')
        return redirect(url_for('main.index'))

    return render_template('auth/register.html')


@auth_bp.route('/connexion', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            next_page = request.args.get('next')
            flash(f'Bon retour, {user.prenom} !', 'success')
            return redirect(next_page or url_for('main.index'))
        flash('Email ou mot de passe incorrect.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/deconnexion')
@login_required
def logout():
    logout_user()
    flash('Vous êtes déconnecté.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/mot-de-passe-oublie', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user  = User.query.filter_by(email=email).first()
        # On répond toujours la même chose (sécurité)
        flash('Si cet email existe, un lien de réinitialisation vous a été envoyé.', 'info')
        if user:
            try:
                send_reset_email(user)
            except Exception:
                pass  # Ne pas exposer l'erreur SMTP
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')


@auth_bp.route('/reinitialiser/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_token(token)
    if not user:
        flash('Ce lien est invalide ou expiré.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        pwd  = request.form.get('password', '')
        pwd2 = request.form.get('password2', '')
        if len(pwd) < 8:
            flash('Le mot de passe doit contenir au moins 8 caractères.', 'danger')
            return render_template('auth/reset_password.html')
        if pwd != pwd2:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return render_template('auth/reset_password.html')
        user.set_password(pwd)
        db.session.commit()
        flash('Mot de passe mis à jour. Vous pouvez vous connecter.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html')


@auth_bp.route('/profil', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.nom    = request.form.get('nom', '').strip()
        current_user.prenom = request.form.get('prenom', '').strip()
        db.session.commit()
        flash('Profil mis à jour.', 'success')
    return render_template('auth/profile.html')
