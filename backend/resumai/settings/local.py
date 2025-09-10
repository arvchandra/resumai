import os

from .base import *

environ.Env.read_env(os.path.join(BASE_DIR, ".env.local"))

# Set environment variables 
OPENAI_API_KEY = env("OPENAI_API_KEY")
SECRET_KEY=env("DJANGO_SECRET_KEY")

# Enable debug mode for local dev
DEBUG = True

# Allow all hosts locally
ALLOWED_HOSTS = ["*"]

# Local database settings
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "resumai",
        "USER": "resumai",
        "PASSWORD": "password",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

# Database to use for GitHub Actions workflow
if os.environ.get('GITHUB_WORKFLOW'):
    DATABASES = {
        'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'github_actions',
           'USER': 'postgres',
           'PASSWORD': 'postgres',
           'HOST': '127.0.0.1',
           'PORT': '5432',
        }
    }



# Cross-Origin Resource Sharing (CORS) settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
]
