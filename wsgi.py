import sys
import os

project_dir = os.path.dirname(os.path.abspath(os.getcwd()))
sys.path.insert(0, '/opt/render/project/src')

from dotenv import load_dotenv
load_dotenv()

from app import create_app
application = create_app('production')
