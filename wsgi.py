# ============================================================
#  Point d'entrée WSGI pour Apache / mod_wsgi
#  Chemin à adapter dans le VirtualHost Apache
# ============================================================
import sys
import os

# Ajouter le dossier du projet au path Python
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Activer le virtualenv si présent
venv_path = os.path.join(project_dir, 'venv', 'lib')
if os.path.exists(venv_path):
    import glob
    python_dirs = glob.glob(os.path.join(venv_path, 'python3*', 'site-packages'))
    if python_dirs:
        sys.path.insert(0, python_dirs[0])

# Charger les variables d'environnement depuis .env
from dotenv import load_dotenv
load_dotenv(os.path.join(project_dir, '.env'))

# Créer l'application Flask
from app import create_app
application = create_app('production')
