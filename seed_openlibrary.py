"""
============================================================
  Script d'import — Open Library API
  Usage : python seed_openlibrary.py
  Importe ~200 vrais livres depuis Open Library
============================================================
"""
import os, sys, time, random, requests
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from run import app
from app import db
from app.models import Book, Category

# ── Couleurs par catégorie ────────────────────────────────
COULEURS = {
    'roman':                   ['#2D4A8A', '#7B3F00', '#B85C00', '#4A2C6E', '#1A3A4A'],
    'science':                 ['#1A6B4A', '#2C5F6E', '#1A4A6B', '#2D6B4A', '#3A5A2A'],
    'histoire':                ['#7B3F00', '#8B2252', '#6B4A00', '#4A3A00', '#5A2A00'],
    'developpement-personnel': ['#6B2D8A', '#8B2252', '#4A2C6E', '#2D4A8A', '#6B4A8A'],
    'informatique':            ['#4A4A8A', '#2D4A8A', '#1A2D5A', '#3A3A7A', '#2A2A6A'],
    'philosophie':             ['#2C5F6E', '#1A4A5A', '#2A5A6A', '#3A6A7A', '#1A3A4A'],
}

BADGES = ['Bestseller', 'Nouveau', 'Classique', 'Top vente', 'Recommandé', None, None, None]

# ── Sujets à rechercher par catégorie ────────────────────
RECHERCHES = {
    'roman': [
        'french literature fiction', 'roman policier', 'classic novel french',
        'victor hugo', 'albert camus', 'gustave flaubert', 'emile zola',
        'alexandre dumas', 'jules verne', 'guy de maupassant',
        'stendhal', 'honore balzac', 'marcel proust', 'andre gide',
    ],
    'science': [
        'physics science popular', 'biology science', 'mathematics popular',
        'stephen hawking', 'richard feynman', 'carl sagan', 'charles darwin',
        'astronomy space', 'chemistry popular science', 'neuroscience brain',
        'evolution biology', 'quantum physics', 'cosmology universe',
    ],
    'histoire': [
        'world history', 'french history', 'ancient history',
        'yuval harari', 'napoleon history', 'world war history',
        'african history', 'medieval history', 'roman empire',
        'renaissance history', 'revolution history', 'colonialism history',
    ],
    'developpement-personnel': [
        'self help personal development', 'motivation success',
        'habits productivity', 'mindfulness meditation',
        'leadership management', 'james clear atomic habits',
        'dale carnegie', 'emotional intelligence', 'positive psychology',
        'stoicism philosophy life', 'time management', 'communication skills',
    ],
    'informatique': [
        'computer science programming', 'python programming',
        'javascript web development', 'algorithms data structures',
        'machine learning artificial intelligence', 'clean code software',
        'linux unix systems', 'database sql', 'web development',
        'cybersecurity hacking', 'software engineering', 'data science',
    ],
    'philosophie': [
        'philosophy classic', 'plato aristotle', 'kant philosophy',
        'nietzsche philosophy', 'existentialism sartre', 'stoicism marcus aurelius',
        'ethics moral philosophy', 'political philosophy', 'epistemology',
        'philosophy of mind', 'french philosophy', 'eastern philosophy',
    ],
}


def fetch_books_for_subject(subject, limit=15):
    """Récupère des livres depuis Open Library pour un sujet donné."""
    url = 'https://openlibrary.org/search.json'
    params = {
        'q': subject,
        'limit': limit,
        'fields': 'title,author_name,first_publish_year,number_of_pages_median,'
                  'isbn,publisher,language,subject,cover_i',
        'lang': 'fre,eng',
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json().get('docs', [])
    except Exception as e:
        print(f"  ⚠️  Erreur réseau pour '{subject}': {e}")
        return []


def import_books():
    with app.app_context():
        # Vérifier les catégories
        categories = {c.slug: c for c in Category.query.all()}
        if not categories:
            print("❌ Aucune catégorie trouvée. Lancez d'abord : flask --app run init-db")
            return

        total_imported = 0
        total_skipped  = 0

        for slug, cat in categories.items():
            if slug not in RECHERCHES:
                continue

            sujets = RECHERCHES[slug]
            print(f"\n📚 Catégorie : {cat.nom} ({len(sujets)} sujets)")
            cat_count = 0

            for sujet in sujets:
                print(f"  🔍 Recherche : {sujet}...", end=' ', flush=True)
                docs = fetch_books_for_subject(sujet, limit=12)
                imported = 0

                for doc in docs:
                    titre = doc.get('title', '').strip()
                    if not titre or len(titre) > 195:
                        continue

                    auteurs = doc.get('author_name', [])
                    auteur  = auteurs[0].strip() if auteurs else 'Auteur inconnu'
                    if len(auteur) > 145:
                        auteur = auteur[:145]

                    # Vérifier doublon
                    if Book.query.filter(
                        db.func.lower(Book.titre)  == titre.lower(),
                        db.func.lower(Book.auteur) == auteur.lower()
                    ).first():
                        total_skipped += 1
                        continue

                    # ISBN
                    isbns = doc.get('isbn', [])
                    isbn  = next((i for i in isbns if len(i) in [10, 13]), None)
                    if isbn and Book.query.filter_by(isbn=isbn).first():
                        isbn = None

                    # Prix aléatoire réaliste
                    prix = round(random.uniform(6.99, 39.99), 2)

                    # Couverture Open Library
                    cover_id  = doc.get('cover_i')
                    couverture = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" \
                                 if cover_id else None

                    # Autres champs
                    annee     = doc.get('first_publish_year')
                    pages     = doc.get('number_of_pages_median')
                    publishers= doc.get('publisher', [])
                    editeur   = publishers[0][:145] if publishers else None
                    langues   = doc.get('language', [])
                    langue    = 'Français' if 'fre' in langues else \
                                'Anglais'  if 'eng' in langues else 'Français'

                    couleur = random.choice(COULEURS.get(slug, ['#2D4A8A']))
                    badge   = random.choice(BADGES)
                    note    = round(random.uniform(3.5, 5.0), 1)
                    nb_avis = random.randint(5, 600)
                    stock   = random.randint(0, 80)
                    featured= random.random() < 0.08  # 8% mis en avant

                    book = Book(
                        titre        = titre,
                        auteur       = auteur,
                        isbn         = isbn,
                        prix         = prix,
                        stock        = stock,
                        category_id  = cat.id,
                        couleur      = couleur,
                        badge        = badge,
                        note_moyenne = note,
                        nb_avis      = nb_avis,
                        annee        = annee if annee and 1000 < annee < 2026 else None,
                        pages        = pages if pages and 10 < pages < 5000 else None,
                        editeur      = editeur,
                        langue       = langue,
                        is_featured  = featured,
                        couverture   = couverture or 'default_cover.jpg',
                        description  = f"Publié{'e' if random.random()>.5 else ''} par "
                                       f"{editeur or 'un éditeur reconnu'}"
                                       f"{' en ' + str(annee) if annee else ''}, "
                                       f"ce livre de {auteur} est une référence dans le domaine "
                                       f"{'de la ' + cat.nom.lower() if cat.nom[0].lower() in 'aeiou' else 'du ' + cat.nom.lower()}.",
                    )
                    db.session.add(book)
                    imported  += 1
                    cat_count += 1
                    total_imported += 1

                try:
                    db.session.commit()
                except Exception:
                    db.session.rollback()

                print(f"{imported} importés")
                time.sleep(0.4)  # Respecter l'API

            print(f"  ✓ Total {cat.nom} : {cat_count} livres")

        print(f"\n{'='*50}")
        print(f"✅ Import terminé !")
        print(f"   • {total_imported} livres importés")
        print(f"   • {total_skipped} doublons ignorés")
        total = Book.query.count()
        print(f"   • {total} livres au total dans la base")
        print(f"{'='*50}\n")


if __name__ == '__main__':
    print("\n🌐 Import depuis Open Library API...")
    print("   (Cela peut prendre 2-3 minutes selon votre connexion)\n")
    import_books()
