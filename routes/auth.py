"""
Routes d'authentification (inscription, connexion, déconnexion)
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from models import db, User
from forms import LoginForm, RegisterForm

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Connexion réussie !', 'success')
            
            # Rediriger vers la page demandée ou l'accueil
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'error')
    
    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Page d'inscription"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        # Vérifier que l'utilisateur n'existe pas déjà
        existing = User.query.filter_by(username=form.username.data).first()
        if existing:
            flash('Ce nom d\'utilisateur est déjà pris.', 'error')
        else:
            # Créer le nouvel utilisateur
            user = User(
                username=form.username.data,
                phone=form.phone.data,
                password=generate_password_hash(form.password.data)
            )
            db.session.add(user)
            db.session.commit()
            
            flash('Inscription réussie ! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    """Déconnexion"""
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('main.index'))