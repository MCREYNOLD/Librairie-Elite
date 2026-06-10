from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from . import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    nom           = db.Column(db.String(80), nullable=False)
    prenom        = db.Column(db.String(80), nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.Enum('user', 'admin'), default='user', nullable=False)
    avatar        = db.Column(db.String(255), default='default.png')
    is_active     = db.Column(db.Boolean, default=True)
    email_verified= db.Column(db.Boolean, default=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    last_login    = db.Column(db.DateTime)
    orders        = db.relationship('Order', backref='user', lazy='dynamic')
    wishlist      = db.relationship('Wishlist', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps(self.email, salt='password-reset')

    @staticmethod
    def verify_reset_token(token):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            email = s.loads(token, salt='password-reset',
                            max_age=current_app.config['RESET_TOKEN_EXPIRES'])
        except Exception:
            return None
        return User.query.filter_by(email=email).first()

    @property
    def full_name(self):
        return f"{self.prenom} {self.nom}"

    def is_admin(self):
        return self.role == 'admin'


class Category(db.Model):
    __tablename__ = 'categories'
    id    = db.Column(db.Integer, primary_key=True)
    nom   = db.Column(db.String(80), unique=True, nullable=False)
    slug  = db.Column(db.String(80), unique=True, nullable=False)
    icone = db.Column(db.String(10), default='📚')
    books = db.relationship('Book', backref='category', lazy='dynamic')


class Book(db.Model):
    __tablename__ = 'books'
    id           = db.Column(db.Integer, primary_key=True)
    titre        = db.Column(db.String(200), nullable=False)
    auteur       = db.Column(db.String(150), nullable=False)
    isbn         = db.Column(db.String(20), unique=True)
    description  = db.Column(db.Text)
    prix         = db.Column(db.Numeric(10, 2), nullable=False)
    stock        = db.Column(db.Integer, default=0)
    couverture   = db.Column(db.String(255), default='default_cover.jpg')
    couleur      = db.Column(db.String(7), default='#2D4A8A')
    annee        = db.Column(db.Integer)
    editeur      = db.Column(db.String(150))
    langue       = db.Column(db.String(30), default='Français')
    pages        = db.Column(db.Integer)
    badge        = db.Column(db.String(30))
    note_moyenne = db.Column(db.Float, default=0.0)
    nb_avis      = db.Column(db.Integer, default=0)
    is_featured  = db.Column(db.Boolean, default=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category_id  = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    order_items  = db.relationship('OrderItem', backref='book', lazy='dynamic')
    wishlist     = db.relationship('Wishlist', backref='book', lazy='dynamic')
    reviews      = db.relationship('Review', backref='book', lazy='dynamic')

    @property
    def en_stock(self):
        return self.stock > 0

    @property
    def stock_status(self):
        if self.stock == 0:  return ('rupture', 'Rupture de stock')
        if self.stock <= 5:  return ('faible', f'Plus que {self.stock} ex.')
        return ('ok', 'En stock')


class Order(db.Model):
    __tablename__ = 'orders'
    id          = db.Column(db.Integer, primary_key=True)
    reference   = db.Column(db.String(20), unique=True, nullable=False)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    statut      = db.Column(db.Enum('en_attente','payee','expediee','livree','annulee'), default='en_attente')
    total       = db.Column(db.Numeric(10, 2), nullable=False)
    adresse     = db.Column(db.Text)
    ville       = db.Column(db.String(100))
    code_postal = db.Column(db.String(20))
    pays        = db.Column(db.String(80))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    items       = db.relationship('OrderItem', backref='order', lazy='joined', cascade='all, delete-orphan')


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id       = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    book_id  = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    prix_u   = db.Column(db.Numeric(10, 2), nullable=False)

    @property
    def sous_total(self):
        return float(self.prix_u) * self.quantite


class Wishlist(db.Model):
    __tablename__ = 'wishlist'
    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'book_id'),)


class Review(db.Model):
    __tablename__ = 'reviews'
    id          = db.Column(db.Integer, primary_key=True)
    book_id     = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    note        = db.Column(db.Integer, nullable=False)
    commentaire = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    user        = db.relationship('User')
    __table_args__ = (db.UniqueConstraint('book_id', 'user_id'),)
