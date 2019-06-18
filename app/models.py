from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

in_carts = db.Table('in_carts',
                    db.Column('buyer_id', db.Integer, db.ForeignKey('user.id')),
                    db.Column('bought_id', db.Integer, db.ForeignKey('product.id'))) 

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    products = db.relationship('Product', backref='seller', lazy='dynamic')
    reviews = db.relationship('Review', backref='reviewer', lazy='dynamic')
    in_cart = db.relationship(
        'Product',
        secondary=in_carts,
        backref="buyinguser",
        lazy='dynamic')

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_to_cart(self, product):
        if not self.check_cart(product):
            self.in_cart.append(product)

    def remove_cart(self, product):
        if self.check_cart(product):
            self.in_cart.remove(product)

    def check_cart(self, product):
        return self.in_cart.filter(
            in_carts.c.bought_id == product.id).count() > 0
    
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    price = db.Column(db.Float, index=True)
    stock = db.Column(db.Integer, index=True)
    avg_ratings = db.Column(db.Float, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    review = db.relationship('Review', backref='product', lazy='dynamic')
    buyers = db.relationship(
        'User',
        secondary=in_carts,
        backref="boughts",
        lazy="dynamic")

    def __repr__(self):
        return '<Product {}>'.format(self.name)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ratings = db.Column(db.String(120), index=True)
    comments = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))

    def __repr__(self):
        return '<Review {}>'.format(self.comments)


