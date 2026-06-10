from flask import Blueprint, render_template, request, abort
from ..models import Book, Category, Review
from .. import db
from flask_login import current_user, login_required

books_bp = Blueprint('books', __name__)


@books_bp.route('/')
def catalogue():
    page      = request.args.get('page', 1, type=int)
    q         = request.args.get('q', '').strip()
    cat_slug  = request.args.get('categorie', '')
    sort      = request.args.get('tri', 'recent')

    query = Book.query
    if q:
        query = query.filter(
            db.or_(Book.titre.ilike(f'%{q}%'),
                   Book.auteur.ilike(f'%{q}%'),
                   Book.isbn.ilike(f'%{q}%')))
    if cat_slug:
        cat = Category.query.filter_by(slug=cat_slug).first_or_404()
        query = query.filter_by(category_id=cat.id)

    if sort == 'prix-asc':   query = query.order_by(Book.prix.asc())
    elif sort == 'prix-desc':query = query.order_by(Book.prix.desc())
    elif sort == 'note':     query = query.order_by(Book.note_moyenne.desc())
    elif sort == 'titre':    query = query.order_by(Book.titre.asc())
    else:                    query = query.order_by(Book.created_at.desc())

    books = query.paginate(page=page, per_page=12, error_out=False)
    categories = Category.query.all()
    return render_template('books/catalogue.html',
                           books=books, q=q, cat_slug=cat_slug,
                           sort=sort, categories=categories)


@books_bp.route('/<int:book_id>')
def detail(book_id):
    book = Book.query.get_or_404(book_id)
    related = Book.query.filter(
        Book.category_id == book.category_id,
        Book.id != book.id
    ).limit(4).all()
    user_review = None
    if current_user.is_authenticated:
        user_review = Review.query.filter_by(
            book_id=book.id, user_id=current_user.id).first()
    return render_template('books/detail.html', book=book,
                           related=related, user_review=user_review)


@books_bp.route('/<int:book_id>/avis', methods=['POST'])
@login_required
def add_review(book_id):
    from flask import redirect, url_for, flash
    book = Book.query.get_or_404(book_id)
    note = request.form.get('note', type=int)
    commentaire = request.form.get('commentaire', '').strip()
    if not note or note < 1 or note > 5:
        flash('Note invalide.', 'danger')
        return redirect(url_for('books.detail', book_id=book_id))
    existing = Review.query.filter_by(book_id=book.id, user_id=current_user.id).first()
    if existing:
        existing.note = note
        existing.commentaire = commentaire
    else:
        r = Review(book_id=book.id, user_id=current_user.id,
                   note=note, commentaire=commentaire)
        db.session.add(r)
    db.session.flush()
    # Recalculer la note moyenne
    reviews = Review.query.filter_by(book_id=book.id).all()
    book.note_moyenne = sum(r.note for r in reviews) / len(reviews)
    book.nb_avis = len(reviews)
    db.session.commit()
    flash('Votre avis a été enregistré.', 'success')
    return redirect(url_for('books.detail', book_id=book_id))
