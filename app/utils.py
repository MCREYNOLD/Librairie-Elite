import os, uuid, random, string
from PIL import Image
from flask import current_app
from flask_mail import Message
from . import mail


def allowed_file(filename):
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS'])


def save_cover(file):
    """Resize et sauvegarde une couverture. Retourne le nom de fichier."""
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    img = Image.open(file)
    img = img.convert('RGB')
    img.thumbnail((400, 600))
    img.save(path, optimize=True, quality=85)
    return filename


def generate_order_ref():
    chars = string.ascii_uppercase + string.digits
    return 'LIB-' + ''.join(random.choices(chars, k=8))


def send_reset_email(user):
    token = user.get_reset_token()
    from flask import url_for
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    msg = Message(
        subject='Réinitialisation de votre mot de passe — Librairie Élite',
        recipients=[user.email]
    )
    msg.html = f"""
    <div style="font-family:Arial,sans-serif;max-width:500px;margin:auto;padding:2rem;border:1px solid #e0e0e0;border-radius:8px">
      <h2 style="color:#2D4A8A">Librairie Élite</h2>
      <p>Bonjour <strong>{user.full_name}</strong>,</p>
      <p>Vous avez demandé la réinitialisation de votre mot de passe. Cliquez sur le bouton ci-dessous :</p>
      <a href="{reset_url}" style="display:inline-block;margin:1.5rem 0;padding:.75rem 2rem;background:#C9A84C;color:white;text-decoration:none;border-radius:6px;font-weight:bold">
        Réinitialiser mon mot de passe
      </a>
      <p style="color:#888;font-size:.85rem">Ce lien expire dans 30 minutes. Si vous n'avez pas fait cette demande, ignorez cet email.</p>
    </div>
    """
    mail.send(msg)


def send_order_confirmation(order, user):
    msg = Message(
        subject=f'Confirmation de commande #{order.reference} — Librairie Élite',
        recipients=[user.email]
    )
    items_html = ''.join(
        f"<tr><td>{item.book.titre}</td><td style='text-align:center'>{item.quantite}</td>"
        f"<td style='text-align:right'>{item.sous_total:.2f} €</td></tr>"
        for item in order.items
    )
    msg.html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:2rem">
      <h2 style="color:#2D4A8A">Merci pour votre commande !</h2>
      <p>Bonjour <strong>{user.full_name}</strong>, votre commande <strong>{order.reference}</strong> a bien été enregistrée.</p>
      <table style="width:100%;border-collapse:collapse;margin:1rem 0">
        <thead><tr style="background:#f5f5f5">
          <th style="padding:.5rem;text-align:left">Livre</th>
          <th style="padding:.5rem">Qté</th>
          <th style="padding:.5rem;text-align:right">Prix</th>
        </tr></thead>
        <tbody>{items_html}</tbody>
        <tfoot><tr style="font-weight:bold;border-top:2px solid #ddd">
          <td colspan="2" style="padding:.75rem">Total</td>
          <td style="padding:.75rem;text-align:right">{float(order.total):.2f} €</td>
        </tr></tfoot>
      </table>
      <p style="color:#888;font-size:.85rem">Livraison à : {order.adresse}, {order.ville} {order.code_postal}, {order.pays}</p>
    </div>
    """
    mail.send(msg)
