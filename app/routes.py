from app import app, db
from flask import render_template, url_for, redirect, flash, request
from flask_login import login_required, current_user, login_user, logout_user
from app.forms import LoginForm, RegistrationForm, ProductForm, ReviewForm
from app.models import User, Product, Review
from werkzeug.urls import url_parse
from flask_paginate import Pagination
from werkzeug.utils import secure_filename
import os

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
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter(Product.seller_id != current_user.id)
    pagination = Pagination(page=page, total=products.count(), record_name='products')
    page_products = products.paginate(page, app.config['PER_PAGE'], False)
    next_url = url_for('index', page=page_products.next_num) if page_products.has_next else None
    prev_url = url_for('index', page=page_products.prev_num) if page_products.has_prev else None
    return render_template('index.html', title="Home", products=page_products.items,
                           next_url=next_url, prev_url=prev_url,
                           pagination=pagination)

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
    product_page = request.args.get('product_page', 1, type=int)
    products = Product.query.filter_by(seller_id=user.id).paginate(product_page, app.config['PER_PAGE'], False)
    
    review_page = request.args.get('review_page', 1, type=int)
    reviews = Review.query.filter_by(user_id = user.id).paginate(review_page, app.config['PER_PAGE'], False)

    product_next_url = url_for('user', product_page=products.next_num, review_page=review_page, username=username) if products.has_next else None
    product_prev_url = url_for('user', product_page=products.prev_num, review_page=review_page, username=username) if products.has_prev else None
    review_next_url = url_for('user', review_page=reviews.next_num, product_page=product_page, username=username) if reviews.has_next else None
    review_prev_url = url_for('user', review_page=reviews.prev_num, product_page=product_page, username=username) if reviews.has_prev else None
    
    return render_template('user.html', user=user, products=products.items, reviews=reviews.items,
                           product_next_url = product_next_url, product_prev_url=product_prev_url,
                           review_next_url = review_next_url, review_prev_url=review_prev_url)
        
@app.route('/newproduct', methods=['GET', 'POST'])
@login_required
def newproduct():
    form = ProductForm()
    if form.validate_on_submit():
        f = form.image.data
        filename = secure_filename(f.filename)
        save_url = os.path.join('app', 'static', filename)
        f.save(save_url)
        product = Product(name=form.name.data,
                          price=float(form.price.data),
                          stock=form.stock.data,
                          seller_id=current_user.id,
                          image_url=filename)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('user', username=current_user.username))
    return render_template('newproduct.html', form=form)

@app.route('/product/<id>')
@login_required
def product(id):
    page = request.args.get('page',1,type=int)
    product = Product.query.filter_by(id=id).first()
    reviews = Review.query.filter_by(product_id=id)
    page_reviews = reviews.paginate(page, app.config['PER_PAGE'], False)
    next_url = url_for('product', id=id, page=page_reviews.next_num) if page_reviews.has_next else None
    prev_url = url_for('product', id=id, page=page_reviews.prev_num) if page_reviews.has_prev else None
    return render_template('product.html', product=product, reviews=page_reviews.items,
                           next_url=next_url, prev_url=prev_url)

@app.route('/review', methods=['GET', 'POST'])
@login_required
def review():
    form = ReviewForm()
    if form.validate_on_submit():
        productId = request.args.get('product_id')
        review = Review(ratings=form.ratings.data,
                        comments=form.comments.data,
                        user_id=current_user.id,
                        product_id= productId)
        all_reviews = Review.query.filter_by(product_id = productId).all()
        no_of_reviews = len(all_reviews)
        product = Product.query.filter_by(id=productId).first()
        if product.avg_ratings is None:
            product.avg_ratings = review.ratings
        else:
            product.avg_ratings = (product.avg_ratings * no_of_reviews + int(review.ratings))/(no_of_reviews + 1)  
        db.session.add(review)
        db.session.commit()
        return redirect(url_for('product', id=request.args.get('product_id')))
    return render_template('review.html', form=form)

@app.route('/deleteproduct/<product_id>')
@login_required
def deleteproduct(product_id):
    product = Product.query.filter_by(id=product_id).first_or_404()
    reviews = Review.query.filter_by(product_id=product_id).all()
    db.session.delete(product)
    for review in reviews:
        db.session.delete(review)
    db.session.commit()
    return redirect(url_for('user',username=current_user.username))

@app.route('/deletereview/<review_id>')
@login_required
def deletereview(review_id):
    review = Review.query.filter_by(id=review_id).first_or_404()
    product = Product.query.filter_by(id=review.product.id).first_or_404()
    all_reviews = Review.query.filter_by(product_id = product.id).all()
    no_of_reviews = len(all_reviews)
    product.avg_ratings = (product.avg_ratings * no_of_reviews - int(review.ratings))/(no_of_reviews - 1)  
    db.session.delete(review)
    db.session.commit()
    prev_url = request.args.get('prev')
    return redirect(prev_url)

@app.route('/addcart/<product_id>')
@login_required
def addcart(product_id):
    prev_url = request.args.get('prev')
    product = Product.query.filter_by(id = product_id).first()
    if product is None:
        flash('Product is not found')
        return redirect(prev_url)
    if product.stock < 1:
        flash('No stock!')
        return redirect(prev_url)
    current_user.add_to_cart(product)
    db.session.commit()
    flash('Added {} to cart!'.format(product.name))
    return redirect(prev_url)

@app.route('/removecart/<product_id>')
@login_required
def removecart(product_id):
    prev_url = request.args.get('prev')
    product = Product.query.filter_by(id = product_id).first()
    if product is None:
        flash('Product is not found')
        return redirect(url_for('cart'))
    current_user.remove_cart(product)
    db.session.commit()
    flash('Removed {} from cart!'.format(product.name))
    return redirect(url_for('cart'))

@app.route('/cart')
@login_required
def cart():
    cart = current_user.in_cart
    return render_template('cart.html', cart=cart)

@app.route('/checkout_cart')
@login_required
def checkout_cart():
    cart = current_user.in_cart
    for product in cart:
        current_user.remove_cart(product)
        product.stock -= 1
        flash('Bought one {}'.format(product.name))
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/clear_cart')
@login_required
def clear_cart():
    cart = current_user.in_cart
    for product in cart:
        current_user.remove_cart(product)
    flash('Your cart has been cleared!')
    db.session.commit()
    return redirect(url_for('index'))
        
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
