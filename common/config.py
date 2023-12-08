import dotenv
import os

dotenv.load_dotenv()

try:
    ROOT_PATH = os.environ["ROOT_PATH"]
except KeyError:
    ROOT_PATH = ""

try:
    GOOGLE_REDIRECT_URI = os.environ["GOOGLE_REDIRECT_URI"]
except KeyError:
    GOOGLE_REDIRECT_URI = "http://localhost:8000/v1/accounts/google/callback"

try:
    LOGOUT_REDIRECT_URI = os.environ["LOGOUT_REDIRECT_URI"]
except KeyError:
    LOGOUT_REDIRECT_URI = "http://localhost:8000/docs"

try:
    LOGIN_REDIRECT_URI = os.environ["LOGIN_REDIRECT_URI"]
except KeyError:
    LOGIN_REDIRECT_URI = "http://localhost:8000/docs"
