import os.path
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

load_dotenv(os.path.join(ROOT_DIR, "../", ".env"))