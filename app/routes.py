from flask import render_template, redirect, url_for, request, flash, session
from app import app, db, bcrypt
from app.forms import LoginForm, RegisterForm
from app.models import User

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'You are now logged in as {user.username}!', 'success')
            return redirect(url_for('user_menu'))
        else:
            flash('Username or password is incorrect.', 'danger')
    return render_template('authorization/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('You are now registered!', 'success')
        return redirect(url_for('login'))
    return render_template('authorization/register.html', form=form)

@app.route('/usermenu')
def user_menu():

    if 'user_id' not in session:
        flash('You need to login first.', 'danger')
        return redirect(url_for('login'))


    user_id = session['user_id']
    user = User.query.get(user_id)

    return render_template('user.menu.html', user=user)
