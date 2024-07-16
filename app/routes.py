from flask import render_template, redirect, url_for, request, flash, session
from app import app, db, bcrypt
from app.forms import RegisterForm, LoginForm
from app.models import User, Card
import datetime

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST':
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session.clear()
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

    if request.method == 'POST' and form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            balance=0,
            card_number=form.card_number.data,
            card_date=form.card_date.data
        )

        db.session.add(new_user)
        db.session.commit()

        new_card = Card(
            card_number=form.card_number.data,
            card_date=form.card_date.data,
            transaction_date=datetime.date.today()
        )

        db.session.add(new_card)
        db.session.commit()

        flash('You are now registered!', 'success')
        return redirect(url_for('login'))

    return render_template('authorization/register.html', form=form)

@app.route('/user_menu', methods=['GET', 'POST'])
def user_menu():
    if 'user_id' not in session:
        flash('You need to login first.', 'danger')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    return render_template('usermenu.html', user=user)

@app.route('/show_balance')
def show_balance():
    if 'user_id' not in session:
        flash('You need to login first.', 'danger')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    return render_template('show.html', balance=user.balance)

@app.route('/add_balance', methods=['GET', 'POST'])
def add_balance():
    if request.method == 'GET':
        return render_template('add.html')

    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    amount = float(request.form['amount'])
    if amount <= 0:
        flash('Amount must be greater than zero.', 'danger')
        return redirect(url_for('add_balance'))

    user.balance += amount
    db.session.commit()

    flash(f'Balance added successfully. New balance is {user.balance}.', 'success')
    return redirect(url_for('user_menu'))

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        flash('You need to login first.', 'danger')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    db.session.delete(user)
    db.session.commit()

    session.clear()
    flash('Your account has been deleted.', 'success')
    return redirect(url_for('login'))

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if request.method == 'GET':
        return render_template('transmoney.html')

    recipient_username = request.form['recipient']
    amount = float(request.form['amount'])

    if amount <= 0:
        flash('Amount must be greater than zero.', 'danger')
        return redirect(url_for('transfer'))

    sender = User.query.get(session['user_id'])
    if not sender:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    recipient = User.query.filter_by(username=recipient_username).first()
    if not recipient:
        flash('Recipient not found.', 'danger')
        return redirect(url_for('transfer'))

    if sender == recipient:
        flash('You cannot transfer money to yourself.', 'danger')
        return redirect(url_for('transfer'))

    if sender.balance < amount:
        flash('Insufficient balance.', 'danger')
        return redirect(url_for('transfer'))

    sender.balance -= amount
    recipient.balance += amount

    db.session.commit()

    flash(f'Transfer of {amount} to {recipient_username} successful.', 'success')
    return redirect(url_for('user_menu'))

@app.route('/transaction_history')
def transaction_history():
    if 'user_id' not in session:
        flash('You need to login first.', 'danger')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    transactions = Card.query.filter_by(card_number=user.card_number).all()

    return render_template('transhistory.html', transactions=transactions)