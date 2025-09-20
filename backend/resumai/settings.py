import environ
import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Check if running in Docker container
IS_RUNNING_IN_CONTAINER = False
if os.getenv("IS_RUNNING_IN_CONTAINER"):
    IS_RUNNING_IN_CONTAINER = True

# Load environment variables from file (only for local development)
# If file not available, env() reads from runtime environment (i.e. Docker)
env = environ.Env()
env_file = os.path.join(BASE_DIR, f".env.local")
if os.path.exists(env_file):
    env.read_env(env_file)

DEBUG = env.bool("DEBUG", default=0)
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",")
OPENAI_API_KEY = env("OPENAI_API_KEY")
SECRET_KEY = env("DJANGO_SECRET_KEY")

# JSON Web Token (JWT) settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tailor",
    "rest_framework",
    "corsheaders",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "resumai.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "resumai.wsgi.application"


# Database settings

DATABASES = {
    "default": {
         "ENGINE": "django.db.backends.{}".format(
             os.getenv("DATABASE_ENGINE", "sqlite3")
         ),
         "NAME": env("POSTGRES_DB", default="resumai"),
         "USER": env("POSTGRES_USER", default="resumai"),
         "PASSWORD": env("POSTGRES_PASSWORD", default="password"),
         "HOST": "db" if IS_RUNNING_IN_CONTAINER else env("DATABASE_HOST", default="localhost"),
         "PORT": env("DATABASE_PORT", default=5432),
     }
}

if os.environ.get("GITHUB_WORKFLOW"):
    DATABASES = {
        "default": {
           "ENGINE": "django.db.backends.postgresql",
           "NAME": env("GIT_POSTGRES_DB"), # Retrieved from Github Secrets/Variables
           "USER": env("GIT_POSTGRES_USER"),# Retrieved from Github Secrets/Variables
           "PASSWORD": env("GIT_POSTGRES_PASSWORD"),# Retrieved from Github Secrets/Variables
           "HOST": "127.0.0.1",
           "PORT": "5432",
        }
    }


# Django REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

# Cross-Origin Resource Sharing (CORS) settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["http://localhost:3000"])

# Password validation
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

# Media storage location
MEDIA_ROOT = BASE_DIR / "uploads"

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
