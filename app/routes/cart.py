from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from ..models import Book

cart_bp = Blueprint('cart', __name__)


def get_cart():
    return session.get('cart', {})

def save_cart(cart):
    session['cart'] = cart
    session.modified = True

def cart_count():
    return sum(v['qty'] for v in get_cart().values())

def cart_total():
    cart = get_cart()
    total = 0.0
    for book_id, item in cart.items():
        book = Book.query.get(int(book_id))
        if book:
            total += float(book.prix) * item['qty']
    return total


@cart_bp.route('/')
def view():
    cart = get_cart()
    items = []
    for book_id, item in cart.items():
        book = Book.query.get(int(book_id))
        if book:
            items.append({'book': book, 'qty': item['qty'],
                          'sous_total': float(book.prix) * item['qty']})
    subtotal = sum(i['sous_total'] for i in items)
    return render_template('cart/cart.html', items=items, subtotal=subtotal)


@cart_bp.route('/ajouter/<int:book_id>', methods=['POST'])
def add(book_id):
    book = Book.query.get_or_404(book_id)
    if not book.en_stock:
        flash('Ce livre est en rupture de stock.', 'warning')
        return redirect(request.referrer or url_for('books.catalogue'))
    cart = get_cart()
    key = str(book_id)
    qty = int(request.form.get('qty', 1))
    if key in cart:
        cart[key]['qty'] = min(cart[key]['qty'] + qty, book.stock)
    else:
        cart[key] = {'qty': min(qty, book.stock)}
    save_cart(cart)
    flash(f'"{book.titre}" ajouté au panier.', 'success')
    return redirect(request.referrer or url_for('books.catalogue'))


@cart_bp.route('/modifier/<int:book_id>', methods=['POST'])
def update(book_id):
    qty  = int(request.form.get('qty', 1))
    cart = get_cart()
    key  = str(book_id)
    if qty <= 0:
        cart.pop(key, None)
    else:
        book = Book.query.get_or_404(book_id)
        cart[key] = {'qty': min(qty, book.stock)}
    save_cart(cart)
    return redirect(url_for('cart.view'))


@cart_bp.route('/supprimer/<int:book_id>')
def remove(book_id):
    cart = get_cart()
    cart.pop(str(book_id), None)
    save_cart(cart)
    flash('Article retiré du panier.', 'info')
    return redirect(url_for('cart.view'))


@cart_bp.route('/vider')
def clear():
    save_cart({})
    return redirect(url_for('cart.view'))
