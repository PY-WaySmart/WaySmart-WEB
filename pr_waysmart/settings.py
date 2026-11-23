from pathlib import Path

from decouple import Csv, config
from django.templatetags.static import static

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1",
    cast=Csv(),
)

INSTALLED_APPS = [
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "pr_waysmart",
    "users",
    "companies",
    "drivers",
    "services",
    "routes",
    "payments",
]
UNFOLD = {
    "SITE_TITLE": "WaySmart Admin",
    "SITE_HEADER": "WaySmart",
    "SITE_SUBHEADER": "Panel de administración",
    "STYLES": [lambda request: static("pr_waysmart/admin.css")],
    "COLORS": {
        "base": {
            "50": "240 247 250",
            "100": "220 234 240",
            "200": "176 204 219",
            "300": "85 149 173",
            "400": "7 95 146",
            "500": "5 79 124",
            "600": "4 60 107",
            "700": "3 47 98",
            "800": "3 40 75",
            "900": "3 29 50",
            "950": "2 24 40",
        },
        "primary": {
            "50": "230 246 255",
            "100": "199 234 250",
            "200": "140 189 246",
            "300": "97 154 251",
            "400": "56 116 250",
            "500": "49 108 233",
            "600": "21 87 217",
            "700": "12 63 162",
            "800": "5 47 98",
            "900": "3 37 75",
            "950": "3 29 50",
        },
    },
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "pr_waysmart.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "pr_waysmart.wsgi.application"
ASGI_APPLICATION = "pr_waysmart.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "es"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "users:login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "users:login"
