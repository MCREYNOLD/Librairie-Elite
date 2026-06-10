import os
from app import create_app, db
from app.models import User, Book, Category, Order, OrderItem, Wishlist, Review

app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Book=Book, Category=Category,
                Order=Order, OrderItem=OrderItem, Review=Review)


@app.cli.command('init-db')
def init_db():
    """Crée toutes les tables et insère des données de démo."""
    db.create_all()
    print('✓ Tables créées.')

    # Catégories de démo
    if not Category.query.first():
        cats = [
            Category(nom='Roman',                  slug='roman',                  icone='📖'),
            Category(nom='Science',                slug='science',                icone='🔬'),
            Category(nom='Histoire',               slug='histoire',               icone='🏛️'),
            Category(nom='Développement personnel',slug='developpement-personnel',icone='✨'),
            Category(nom='Informatique',           slug='informatique',           icone='💻'),
            Category(nom='Philosophie',            slug='philosophie',            icone='🧠'),
        ]
        db.session.add_all(cats)
        db.session.commit()
        print('✓ Catégories créées.')

    # Compte admin de démo
    if not User.query.filter_by(email='admin@librairie.com').first():
        admin = User(nom='Admin', prenom='Super', email='admin@librairie.com', role='admin')
        admin.set_password('Admin1234!')
        db.session.add(admin)
        db.session.commit()
        print('✓ Admin créé : admin@librairie.com / Admin1234!')

    # Livres de démo
    if not Book.query.first():
        roman_id  = Category.query.filter_by(slug='roman').first().id
        sci_id    = Category.query.filter_by(slug='science').first().id
        hist_id   = Category.query.filter_by(slug='histoire').first().id
        dev_id    = Category.query.filter_by(slug='developpement-personnel').first().id
        info_id   = Category.query.filter_by(slug='informatique').first().id
        philo_id  = Category.query.filter_by(slug='philosophie').first().id

        livres = [
            Book(titre="L'Étranger", auteur="Albert Camus", prix=9.99, stock=42,
                 category_id=roman_id, couleur='#2D4A8A', badge='Classique',
                 note_moyenne=4.8, nb_avis=312, is_featured=True,
                 description="Roman existentialiste d'Albert Camus publié en 1942. Meursault, un Français vivant en Algérie, apprend la mort de sa mère et tue un Arabe sur la plage."),
            Book(titre="Une brève histoire du temps", auteur="Stephen Hawking", prix=14.99, stock=18,
                 category_id=sci_id, couleur='#1A6B4A', badge='Bestseller',
                 note_moyenne=4.7, nb_avis=201, is_featured=True,
                 description="De la formation de l'univers jusqu'aux trous noirs, Stephen Hawking explore les grandes questions de la physique moderne avec une clarté remarquable."),
            Book(titre="Sapiens", auteur="Yuval Noah Harari", prix=22.00, stock=30,
                 category_id=hist_id, couleur='#7B3F00', badge='Bestseller',
                 note_moyenne=4.9, nb_avis=548, is_featured=True,
                 description="Une brève histoire de l'humanité. Comment l'Homo sapiens est-il devenu l'espèce dominante sur Terre ?"),
            Book(titre="Atomic Habits", auteur="James Clear", prix=18.50, stock=55,
                 category_id=dev_id, couleur='#6B2D8A', badge='Top vente',
                 note_moyenne=4.8, nb_avis=423, is_featured=True,
                 description="Un guide pratique pour construire de bonnes habitudes et se débarrasser des mauvaises. La méthode des 1% de mieux chaque jour."),
            Book(titre="Clean Code", auteur="Robert C. Martin", prix=34.99, stock=8,
                 category_id=info_id, couleur='#4A4A8A',
                 note_moyenne=4.6, nb_avis=187,
                 description="Les principes, patterns et pratiques pour écrire du code propre et maintenable."),
            Book(titre="Le Petit Prince", auteur="Antoine de Saint-Exupéry", prix=7.50, stock=80,
                 category_id=roman_id, couleur='#B85C00', badge='Classique',
                 note_moyenne=4.9, nb_avis=891,
                 description="Le conte philosophique le plus lu au monde. Un aviateur rencontre un mystérieux petit garçon dans le désert."),
            Book(titre="Homo Deus", auteur="Yuval Noah Harari", prix=21.00, stock=25,
                 category_id=hist_id, couleur='#2C5F6E',
                 note_moyenne=4.5, nb_avis=156,
                 description="Une brève histoire de l'avenir. Que deviendra l'humanité à l'ère de l'intelligence artificielle ?"),
            Book(titre="Le pouvoir du moment présent", auteur="Eckhart Tolle", prix=16.00, stock=3,
                 category_id=dev_id, couleur='#8B2252',
                 note_moyenne=4.4, nb_avis=98,
                 description="Un guide spirituel vers l'éveil. Comment vivre pleinement dans l'instant présent."),
            Book(titre="JavaScript: The Good Parts", auteur="Douglas Crockford", prix=29.99, stock=12,
                 category_id=info_id, couleur='#1A6B4A', badge='Référence',
                 note_moyenne=4.7, nb_avis=234,
                 description="Les meilleures parties du langage JavaScript expliquées avec précision par son grand architecte."),
            Book(titre="Les Misérables", auteur="Victor Hugo", prix=12.00, stock=60,
                 category_id=roman_id, couleur='#7B3F00', badge='Classique',
                 note_moyenne=4.8, nb_avis=502,
                 description="Le chef-d'œuvre de Victor Hugo. Jean Valjean, ancien forçat, se rachète à travers une vie de bonté et de sacrifice."),
        ]
        db.session.add_all(livres)
        db.session.commit()
        print(f'✓ {len(livres)} livres de démo créés.')

    print('\n🚀 Base de données prête. Lancez : flask run')


if __name__ == '__main__':
    app.run(debug=True)
