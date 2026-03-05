from app import db
from flask import render_template, flash, redirect, url_for
import sqlalchemy as sqla
from app.main.models import Admin
from app.auth.auth_forms import LoginForm
from flask_login import login_user, current_user, logout_user, login_required
from app.auth import auth_blueprint as auth


@auth.route('/admin/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    lForm = LoginForm()
    if lForm.validate_on_submit():
        query = sqla.Select(Admin).where(Admin.username == lForm.username.data)
        admin = db.session.scalars(query).first()
        if (admin is None) or (admin.check_password(lForm.password.data) == False):
            return redirect(url_for('auth.login'))
        login_user(admin, remember= lForm.remember_me.data)
        flash('Welcome, {}'.format(current_user.username))
        return redirect(url_for('main.index'))
    return render_template('login.html', form = lForm) 

@auth.route("/admin/logout", methods = ['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

