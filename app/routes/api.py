from flask import Blueprint, jsonify, request
from ..models import Book, Category

api_bp = Blueprint('api', __name__)

@api_bp.route('/livres')
def api_books():
    q = request.args.get('q', '').strip()
    from .. import db
    query = Book.query
    if q:
        query = query.filter(
            db.or_(Book.titre.ilike(f'%{q}%'), Book.auteur.ilike(f'%{q}%')))
    books = query.limit(20).all()
    return jsonify([{
        'id': b.id, 'titre': b.titre, 'auteur': b.auteur,
        'prix': float(b.prix), 'stock': b.stock,
        'note': b.note_moyenne, 'couverture': b.couverture
    } for b in books])

@api_bp.route('/categories')
def api_categories():
    cats = Category.query.all()
    return jsonify([{'id': c.id, 'nom': c.nom, 'slug': c.slug} for c in cats])
