from app import app, db
from flask import render_template, url_for, redirect, flash, request
from flask_login import login_required, current_user, login_user, logout_user
from app.forms import LoginForm, RegistrationForm, ProductForm
from app.models import User
from werkzeug.urls import url_parse

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("The username or password is not correct")
            return redirect(url_for('index'))
        login_user(user)
        next_url = request.args.get('next')
        if not next_url or url_parse(next_url).netloc != '':
            return redirect(url_for('index'))
        return redirect(next_url)
    return render_template('login.html', title='Sign-In', form=form)

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title="Home")

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been registered!')
        return redirect(url_for('login'))
    return render_template('registration.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    products = [
        {'seller': user, 'name':'Ball', 'price': 9.99, 'stock': 5},
        {'seller': user, 'name':'Flowers', 'price': 10.00, 'stock': 20}
    ]
    return render_template('user.html', user=user, products=products)
        
@app.route('/newproduct', methods=['GET', 'POST'])
@login_required
def newproduct():
    form = ProductForm()
    if form.validate_on_submit:
        product = Product(name=form.name.data)
    return render_template(url_for('newproduct.html', form=form))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
