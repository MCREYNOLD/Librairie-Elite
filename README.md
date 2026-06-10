# Librairie Élite — Guide d'installation XAMPP (Linux / Mac)

## Stack technique
- **Backend** : Python 3 + Flask
- **Base de données** : MySQL (via XAMPP)
- **Serveur** : Apache + mod_wsgi (via XAMPP)
- **Templates** : Jinja2

---

## Prérequis

| Outil | Version minimale |
|---|---|
| Python | 3.9+ |
| XAMPP | 8.x |
| pip | 23+ |

---

## Installation rapide (script automatique)

```bash
# 1. Copier le projet dans le dossier htdocs de XAMPP
sudo cp -r librairie/ /opt/lampp/htdocs/librairie
cd /opt/lampp/htdocs/librairie

# 2. Lancer le script d'installation
bash setup_xampp.sh
```

Le script fait automatiquement :
- Création du virtualenv Python
- Installation de toutes les dépendances (`requirements.txt`)
- Installation de `mod_wsgi`
- Création de la base de données MySQL
- Création des tables + données de démo
- Configuration du VirtualHost Apache
- Ajout de `librairie.local` dans `/etc/hosts`

---

## Installation manuelle (étape par étape)

### Étape 1 — Copier le projet

```bash
sudo cp -r librairie/ /opt/lampp/htdocs/librairie
cd /opt/lampp/htdocs/librairie
```

### Étape 2 — Créer le virtualenv et installer les dépendances

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install mod-wsgi
```

### Étape 3 — Configurer l'environnement

```bash
cp .env.example .env
nano .env   # Remplir DB_PASSWORD, MAIL_USERNAME, MAIL_PASSWORD
```

Contenu minimal du `.env` :
```env
SECRET_KEY=une_cle_aleatoire_longue
DB_HOST=localhost
DB_PORT=3306
DB_NAME=librairie_db
DB_USER=librairie_user
DB_PASSWORD=librairie_pass
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=votre@gmail.com
MAIL_PASSWORD=mot_de_passe_application_gmail
FLASK_ENV=production
```

### Étape 4 — Créer la base de données MySQL

Ouvrir phpMyAdmin (`http://localhost/phpmyadmin`) ou via terminal :

```sql
CREATE DATABASE librairie_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'librairie_user'@'localhost' IDENTIFIED BY 'librairie_pass';
GRANT ALL PRIVILEGES ON librairie_db.* TO 'librairie_user'@'localhost';
FLUSH PRIVILEGES;
```

### Étape 5 — Créer les tables et données de démo

```bash
cd /opt/lampp/htdocs/librairie
source venv/bin/activate
flask --app run init-db
```

Résultat attendu :
```
✓ Tables créées.
✓ Catégories créées.
✓ Admin créé : admin@librairie.com / Admin1234!
✓ 10 livres de démo créés.
```

### Étape 6 — Configurer mod_wsgi dans Apache

**Trouver le chemin de mod_wsgi :**
```bash
source venv/bin/activate
mod_wsgi-express module-location
# Exemple : /opt/lampp/htdocs/librairie/venv/lib/python3.11/site-packages/mod_wsgi/server/mod_wsgi-py311...so
```

**Ajouter dans `/opt/lampp/etc/httpd.conf` :**
```apache
LoadModule wsgi_module /chemin/retourné/ci-dessus.so
```

**Activer les VirtualHosts dans `/opt/lampp/etc/httpd.conf` :**
```apache
# Décommenter cette ligne :
Include etc/extra/httpd-vhosts.conf
```

### Étape 7 — Ajouter le VirtualHost Apache

Copier `librairie.conf` dans les vhosts :
```bash
sudo cat librairie.conf >> /opt/lampp/etc/extra/httpd-vhosts.conf
```

> ⚠️ Adaptez le chemin `Define PROJ /opt/lampp/htdocs/librairie` si différent.

### Étape 8 — Ajouter le domaine local

```bash
sudo nano /etc/hosts
# Ajouter la ligne :
127.0.0.1  librairie.local
```

### Étape 9 — Redémarrer XAMPP

```bash
sudo /opt/lampp/lampp restart
```

### Étape 10 — Ouvrir dans le navigateur

```
http://librairie.local
```

---

## Compte administrateur de démo

| Champ | Valeur |
|---|---|
| Email | `admin@librairie.com` |
| Mot de passe | `Admin1234!` |
| URL admin | `http://librairie.local/admin` |

---

## Lancer en mode développement (sans Apache)

```bash
cd /opt/lampp/htdocs/librairie
source venv/bin/activate
flask --app run run --debug
# Accessible sur http://localhost:5000
```

---

## Structure des URLs

| URL | Description |
|---|---|
| `/` | Page d'accueil |
| `/livres/` | Catalogue |
| `/livres/<id>` | Détail d'un livre |
| `/panier/` | Panier |
| `/commandes/paiement` | Checkout |
| `/auth/inscription` | Créer un compte |
| `/auth/connexion` | Se connecter |
| `/auth/mot-de-passe-oublie` | Mot de passe oublié |
| `/auth/reinitialiser/<token>` | Réinitialiser le MDP |
| `/admin/` | Panel admin |

---

## Dépannage

**Erreur 403 Forbidden**
→ Vérifier les permissions : `sudo chmod -R 755 /opt/lampp/htdocs/librairie`

**Erreur 500 Internal Server Error**
→ Consulter les logs : `tail -f /opt/lampp/logs/librairie_error.log`

**`ModuleNotFoundError`**
→ Vérifier que `python-home` dans le VirtualHost pointe vers votre `venv`

**Emails non reçus**
→ Gmail : activer l'authentification à 2 facteurs et créer un "Mot de passe d'application"

**Port 80 occupé**
→ `sudo fuser -k 80/tcp` puis `sudo /opt/lampp/lampp start`
