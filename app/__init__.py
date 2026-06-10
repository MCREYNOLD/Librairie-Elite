import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'warning'


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')
    app.config.from_object(config[config_name])

    # Extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Blueprints
    from .routes.main   import main_bp
    from .routes.auth   import auth_bp
    from .routes.books  import books_bp
    from .routes.cart   import cart_bp
    from .routes.orders import orders_bp
    from .routes.admin  import admin_bp
    from .routes.api    import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp,   url_prefix='/auth')
    app.register_blueprint(books_bp,  url_prefix='/livres')
    app.register_blueprint(cart_bp,   url_prefix='/panier')
    app.register_blueprint(orders_bp, url_prefix='/commandes')
    app.register_blueprint(admin_bp,  url_prefix='/admin')
    app.register_blueprint(api_bp,    url_prefix='/api')

    # Créer dossier uploads
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # User loader
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Inject categories in all templates
    from .models import Category

    @app.context_processor
    def inject_globals():
        categories = Category.query.order_by(Category.nom).all()
        return dict(categories=categories)

    return app
