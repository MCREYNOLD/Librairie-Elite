from flask import Blueprint, render_template
from ..models import Book, Category

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    featured = Book.query.filter_by(is_featured=True).limit(6).all()
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
