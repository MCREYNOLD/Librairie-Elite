from flask import Blueprint, render_template
from ..models import Book, Category
from sqlalchemy import true

main_bp = Blueprint('main', name)

@main_bp.route('/')
def index():
    featured = Book.query.filter(Book.is_featured == true()).limit(6).all()
    nouveautes = Book.query.order_by(Book.created_at.desc()).limit(8).all()
    bestsellers = Book.query.order_by(Book.note_moyenne.desc()).limit(8).all()
    categories = Category.query.all()
    return render_template('main/index.html',
                           featured=featured,
                           nouveautes=nouveautes,
                           bestsellers=bestsellers,
                           categories=categories)

@main_bp.route('/a-propos')
def about():
    return render_template('main/about.html')
