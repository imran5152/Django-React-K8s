"""
Django settings for the College app.

The app is a small JSON API backed by MongoDB, so it does not use the Django
ORM, admin, sessions or auth. All configuration comes from environment
variables, which is how the Kubernetes ConfigMap and Secret feed it.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-insecure-key-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")
    if host.strip()
]

INSTALLED_APPS = ["students"]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "college_project.urls"
WSGI_APPLICATION = "college_project.wsgi.application"

# No SQL database: data lives in MongoDB (see students/db.py).
DATABASES = {}

# Nginx forwards /students and /students/<id> exactly as the browser sent them.
APPEND_SLASH = False

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# MongoDB
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/college")
MONGODB_DB = os.environ.get("MONGODB_DB", "college")
MONGODB_TIMEOUT_MS = int(os.environ.get("MONGODB_TIMEOUT_MS", "3000"))

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
