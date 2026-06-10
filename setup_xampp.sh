#!/bin/bash
# ============================================================
#  Script d'installation automatique — Librairie Élite
#  Usage : bash setup_xampp.sh
#  À exécuter depuis le dossier du projet (ex: /opt/lampp/htdocs/librairie)
# ============================================================

set -e  # Arrêter si une commande échoue

PROJ_DIR="$(cd "$(dirname "$0")" && pwd)"
XAMPP_DIR="/opt/lampp"   # Changer si XAMPP est ailleurs (Mac: /Applications/XAMPP/xamppfiles)
VENV_DIR="$PROJ_DIR/venv"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   Librairie Élite — Installation XAMPP   ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "📁 Dossier projet : $PROJ_DIR"
echo "📁 Dossier XAMPP  : $XAMPP_DIR"
echo ""

# ── 1. Vérifier Python 3 ─────────────────────────────────────
echo "[ 1/7 ] Vérification de Python 3..."
if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 non trouvé. Installez-le d'abord."
    exit 1
fi
PYTHON_VER=$(python3 --version)
echo "       ✓ $PYTHON_VER"

# ── 2. Créer le virtualenv ───────────────────────────────────
echo "[ 2/7 ] Création du virtualenv..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "       ✓ Virtualenv créé dans $VENV_DIR"
else
    echo "       ✓ Virtualenv déjà existant"
fi

# ── 3. Installer les dépendances ─────────────────────────────
echo "[ 3/7 ] Installation des dépendances Python..."
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install -r "$PROJ_DIR/requirements.txt" -q
"$VENV_DIR/bin/pip" install mod-wsgi -q
echo "       ✓ Dépendances installées"

# ── 4. Créer le fichier .env ─────────────────────────────────
echo "[ 4/7 ] Configuration de l'environnement..."
if [ ! -f "$PROJ_DIR/.env" ]; then
    cp "$PROJ_DIR/.env.example" "$PROJ_DIR/.env"
    # Générer une SECRET_KEY aléatoire
    SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/change_this_to_a_random_secret_key/$SECRET/" "$PROJ_DIR/.env"
    echo "       ✓ Fichier .env créé — Éditez DB_USER / DB_PASSWORD / MAIL_USERNAME"
else
    echo "       ✓ Fichier .env déjà existant"
fi

# ── 5. Créer la base de données MySQL via XAMPP ──────────────
echo "[ 5/7 ] Création de la base de données MySQL..."
MYSQL="$XAMPP_DIR/bin/mysql"
if [ ! -f "$MYSQL" ]; then
    echo "       ⚠️  mysql non trouvé dans $XAMPP_DIR/bin. Créez manuellement :"
    echo "          CREATE DATABASE librairie_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    echo "          CREATE USER 'librairie_user'@'localhost' IDENTIFIED BY 'librairie_pass';"
    echo "          GRANT ALL ON librairie_db.* TO 'librairie_user'@'localhost';"
else
    "$MYSQL" -u root -e "
    CREATE DATABASE IF NOT EXISTS librairie_db
      CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    CREATE USER IF NOT EXISTS 'librairie_user'@'localhost'
      IDENTIFIED BY 'librairie_pass';
    GRANT ALL PRIVILEGES ON librairie_db.* TO 'librairie_user'@'localhost';
    FLUSH PRIVILEGES;" 2>/dev/null && echo "       ✓ Base de données prête" || \
    echo "       ⚠️  Vérifiez que XAMPP MySQL est démarré (sudo $XAMPP_DIR/lampp start)"
fi

# ── 6. Initialiser les tables et données de démo ─────────────
echo "[ 6/7 ] Initialisation des tables Flask..."
cd "$PROJ_DIR"
FLASK_APP=run.py "$VENV_DIR/bin/flask" init-db 2>/dev/null && \
    echo "       ✓ Tables créées + données de démo insérées" || \
    echo "       ⚠️  Vérifiez la connexion MySQL dans .env puis relancez : flask init-db"

# ── 7. Configurer Apache mod_wsgi ────────────────────────────
echo "[ 7/7 ] Configuration Apache..."

# Adapter le chemin dans librairie.conf
sed "s|/opt/lampp/htdocs/librairie|$PROJ_DIR|g" \
    "$PROJ_DIR/librairie.conf" > /tmp/librairie_vhost.conf

VHOSTS_CONF="$XAMPP_DIR/etc/extra/httpd-vhosts.conf"
if [ -f "$VHOSTS_CONF" ]; then
    if grep -q "librairie.local" "$VHOSTS_CONF" 2>/dev/null; then
        echo "       ✓ VirtualHost déjà présent dans httpd-vhosts.conf"
    else
        cat /tmp/librairie_vhost.conf >> "$VHOSTS_CONF"
        echo "       ✓ VirtualHost ajouté à httpd-vhosts.conf"
    fi
else
    echo "       ⚠️  Copiez manuellement le fichier librairie.conf dans :"
    echo "          $VHOSTS_CONF"
fi

# Ajouter mod_wsgi au chargement Apache si besoin
HTTPD_CONF="$XAMPP_DIR/etc/httpd.conf"
WSGI_SO="$("$VENV_DIR/bin/mod_wsgi-express" module-location 2>/dev/null || echo '')"
if [ -n "$WSGI_SO" ] && [ -f "$HTTPD_CONF" ]; then
    if ! grep -q "mod_wsgi" "$HTTPD_CONF"; then
        echo "LoadModule wsgi_module $WSGI_SO" | sudo tee -a "$HTTPD_CONF" > /dev/null
        echo "       ✓ mod_wsgi ajouté à httpd.conf"
    else
        echo "       ✓ mod_wsgi déjà chargé"
    fi
fi

# Activer httpd-vhosts.conf si commenté
if grep -q "#Include etc/extra/httpd-vhosts.conf" "$HTTPD_CONF" 2>/dev/null; then
    sudo sed -i 's|#Include etc/extra/httpd-vhosts.conf|Include etc/extra/httpd-vhosts.conf|' "$HTTPD_CONF"
    echo "       ✓ httpd-vhosts.conf activé dans httpd.conf"
fi

# ── Ajouter librairie.local dans /etc/hosts ──────────────────
if ! grep -q "librairie.local" /etc/hosts; then
    echo "127.0.0.1  librairie.local" | sudo tee -a /etc/hosts > /dev/null
    echo "       ✓ librairie.local ajouté à /etc/hosts"
else
    echo "       ✓ librairie.local déjà dans /etc/hosts"
fi

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║           Installation terminée !        ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "  1. Démarrer XAMPP    : sudo $XAMPP_DIR/lampp restart"
echo "  2. Ouvrir dans le navigateur : http://librairie.local"
echo ""
echo "  Compte admin de démo :"
echo "    Email    : admin@librairie.com"
echo "    Mot de passe : Admin1234!"
echo ""
echo "  Pour lancer en mode dev sans Apache :"
echo "    source venv/bin/activate"
echo "    flask --app run run --debug"
echo ""
