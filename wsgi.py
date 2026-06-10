import sys
import os

project_dir = os.path.dirname(os.path.abspath(file))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(project_dir, '.env'))

from app import create_app
application = create_app('production')
