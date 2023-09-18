"""
Django settings for voxpop project.
"""
from pathlib import Path

from environs import Env


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()
env.read_env()

SHARED_SECRET_JWT=env.str("SHARED_SECRET_JWT")
SECRET_KEY = env.str("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = CORS_ORIGIN_WHITELIST = env.list("CSRF_TRUSTED_ORIGINS")
PLUGON_HOSTNAME = env.str("PLUGON_HOSTNAME")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "daphne",
    "django.contrib.staticfiles",
    "corsheaders",
    "voxpop",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]


LOCALE_PATHS = [
    "locale/"
]

ROOT_URLCONF = "voxpop_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "voxpop_project" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ASGI_APPLICATION = "voxpop_project.asgi.application"
WSGI_APPLICATION = "voxpop_project.wsgi.application"

DATABASES = {
    "default": env.dj_db_url("DATABASE_URL"),
}

LANGUAGE_CODE = env.str("LANGUAGE_CODE")

TIME_ZONE = env.str("TIME_ZONE")

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = env.list("ALLOWED_CORS_HOSTS")
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_METHODS = [
    "GET",
    "POST",
    "OPTIONS",
]
