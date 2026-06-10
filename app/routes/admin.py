from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from .. import db
from ..models import Book, Category, User, Order
from ..utils import allowed_file, save_cover

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@admin_required
def dashboard():
    stats = {
        'books':   Book.query.count(),
        'users':   User.query.count(),
        'orders':  Order.query.count(),
        'revenue': db.session.query(db.func.sum(Order.total)).scalar() or 0,
    }
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    low_stock     = Book.query.filter(Book.stock <= 5).order_by(Book.stock.asc()).limit(10).all()
    return render_template('admin/dashboard.html', stats=stats,
                           recent_orders=recent_orders, low_stock=low_stock)


# ── Livres ────────────────────────────────────────────────
@admin_bp.route('/livres')
@admin_required
def books():
    page = request.args.get('page', 1, type=int)
    books = Book.query.order_by(Book.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/books.html', books=books)


@admin_bp.route('/livres/nouveau', methods=['GET', 'POST'])
@admin_required
def book_new():
    categories = Category.query.all()
    if request.method == 'POST':
        couverture = 'default_cover.jpg'
        if 'couverture' in request.files:
            f = request.files['couverture']
            if f and f.filename and allowed_file(f.filename):
                couverture = save_cover(f)
        book = Book(
            titre       = request.form['titre'],
            auteur      = request.form['auteur'],
            prix        = float(request.form['prix']),
            stock       = int(request.form['stock']),
            category_id = int(request.form['category_id']),
            description = request.form.get('description', ''),
            isbn        = request.form.get('isbn') or None,
            annee       = int(request.form['annee']) if request.form.get('annee') else None,
            editeur     = request.form.get('editeur', ''),
            langue      = request.form.get('langue', 'Français'),
            pages       = int(request.form['pages']) if request.form.get('pages') else None,
            badge       = request.form.get('badge') or None,
            couleur     = request.form.get('couleur', '#2D4A8A'),
            is_featured = 'is_featured' in request.form,
            couverture  = couverture,
        )
        db.session.add(book)
        db.session.commit()
        flash('Livre ajouté.', 'success')
        return redirect(url_for('admin.books'))
    return render_template('admin/book_form.html', book=None, categories=categories)


@admin_bp.route('/livres/<int:book_id>/modifier', methods=['GET', 'POST'])
@admin_required
def book_edit(book_id):
    book = Book.query.get_or_404(book_id)
    categories = Category.query.all()
    if request.method == 'POST':
        if 'couverture' in request.files:
            f = request.files['couverture']
            if f and f.filename and allowed_file(f.filename):
                book.couverture = save_cover(f)
        book.titre       = request.form['titre']
        book.auteur      = request.form['auteur']
        book.prix        = float(request.form['prix'])
        book.stock       = int(request.form['stock'])
        book.category_id = int(request.form['category_id'])
        book.description = request.form.get('description', '')
        book.isbn        = request.form.get('isbn') or None
        book.annee       = int(request.form['annee']) if request.form.get('annee') else None
        book.editeur     = request.form.get('editeur', '')
        book.langue      = request.form.get('langue', 'Français')
        book.pages       = int(request.form['pages']) if request.form.get('pages') else None
        book.badge       = request.form.get('badge') or None
        book.couleur     = request.form.get('couleur', '#2D4A8A')
        book.is_featured = 'is_featured' in request.form
        db.session.commit()
        flash('Livre mis à jour.', 'success')
        return redirect(url_for('admin.books'))
    return render_template('admin/book_form.html', book=book, categories=categories)


@admin_bp.route('/livres/<int:book_id>/supprimer', methods=['POST'])
@admin_required
def book_delete(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Livre supprimé.', 'info')
    return redirect(url_for('admin.books'))


# ── Utilisateurs ─────────────────────────────────────────
@admin_bp.route('/utilisateurs')
@admin_required
def users():
    page  = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/users.html', users=users)


@admin_bp.route('/utilisateurs/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Vous ne pouvez pas modifier votre propre rôle.', 'warning')
    else:
        user.role = 'user' if user.role == 'admin' else 'admin'
        db.session.commit()
        flash(f'Rôle de {user.full_name} mis à jour.', 'success')
    return redirect(url_for('admin.users'))


# ── Commandes ─────────────────────────────────────────────
@admin_bp.route('/commandes')
@admin_required
def orders():
    page   = request.args.get('page', 1, type=int)
    orders = Order.query.order_by(Order.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/orders.html', orders=orders)


@admin_bp.route('/commandes/<int:order_id>/statut', methods=['POST'])
@admin_required
def order_status(order_id):
    order  = Order.query.get_or_404(order_id)
    statut = request.form.get('statut')
    valid  = ['en_attente', 'payee', 'expediee', 'livree', 'annulee']
    if statut in valid:
        order.statut = statut
        db.session.commit()
        flash('Statut mis à jour.', 'success')
    return redirect(url_for('admin.orders'))


# ── Catégories ────────────────────────────────────────────
@admin_bp.route('/categories', methods=['GET', 'POST'])
@admin_required
def categories():
    if request.method == 'POST':
        import re
        nom  = request.form.get('nom', '').strip()
        slug = re.sub(r'[^a-z0-9]+', '-', nom.lower()).strip('-')
        icone= request.form.get('icone', '📚')
        if nom and not Category.query.filter_by(slug=slug).first():
            db.session.add(Category(nom=nom, slug=slug, icone=icone))
            db.session.commit()
            flash('Catégorie ajoutée.', 'success')
        else:
            flash('Nom invalide ou déjà existant.', 'danger')
    cats = Category.query.order_by(Category.nom).all()
    return render_template('admin/categories.html', categories=cats)
