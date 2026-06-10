from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from .. import db
from ..models import Book, Order, OrderItem
from ..utils import generate_order_ref, send_order_confirmation

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/paiement', methods=['GET', 'POST'])
@login_required
def checkout():
    from .cart import get_cart, save_cart, cart_total
    cart = get_cart()
    if not cart:
        flash('Votre panier est vide.', 'warning')
        return redirect(url_for('cart.view'))

    items = []
    for book_id, item in cart.items():
        book = Book.query.get(int(book_id))
        if book:
            items.append({'book': book, 'qty': item['qty'],
                          'sous_total': float(book.prix) * item['qty']})
    subtotal = sum(i['sous_total'] for i in items)
    total_ttc = subtotal * 1.20

    if request.method == 'POST':
        adresse     = request.form.get('adresse', '').strip()
        ville       = request.form.get('ville', '').strip()
        code_postal = request.form.get('code_postal', '').strip()
        pays        = request.form.get('pays', '').strip()

        if not all([adresse, ville, code_postal, pays]):
            flash('Veuillez compléter votre adresse de livraison.', 'danger')
            return render_template('orders/checkout.html', items=items,
                                   subtotal=subtotal, total=total_ttc)

        # Vérifier et décrémenter le stock
        for item_data in items:
            book = item_data['book']
            if book.stock < item_data['qty']:
                flash(f'Stock insuffisant pour "{book.titre}".', 'danger')
                return redirect(url_for('cart.view'))

        order = Order(
            reference   = generate_order_ref(),
            user_id     = current_user.id,
            total       = total_ttc,
            adresse     = adresse,
            ville       = ville,
            code_postal = code_postal,
            pays        = pays,
            statut      = 'payee'
        )
        db.session.add(order)
        db.session.flush()

        for item_data in items:
            book = item_data['book']
            oi = OrderItem(order_id=order.id, book_id=book.id,
                           quantite=item_data['qty'], prix_u=book.prix)
            db.session.add(oi)
            book.stock -= item_data['qty']

        db.session.commit()
        save_cart({})

        try:
            send_order_confirmation(order, current_user)
        except Exception:
            pass

        flash(f'Commande {order.reference} confirmée ! Merci pour votre achat.', 'success')
        return redirect(url_for('orders.confirmation', order_id=order.id))

    return render_template('orders/checkout.html', items=items,
                           subtotal=subtotal, total=total_ttc)


@orders_bp.route('/confirmation/<int:order_id>')
@login_required
def confirmation(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return render_template('orders/confirmation.html', order=order)


@orders_bp.route('/mes-commandes')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id)\
                        .order_by(Order.created_at.desc()).all()
    return render_template('orders/my_orders.html', orders=orders)


@orders_bp.route('/<int:order_id>')
@login_required
def detail(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return render_template('orders/detail.html', order=order)
