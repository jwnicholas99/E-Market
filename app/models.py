from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    products = db.relationship('Product', backref='seller', lazy='dynamic')
    reviews = db.relationship('Review', backref='reviewer', lazy='dynamic')

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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

    def __repr__(self):
        return '<Product {}>'.format(self.name)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gradings = db.Column(db.Float)
    comments = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))

    def __repr__(self):
        return '<Review {}>'.format(self.comments)
