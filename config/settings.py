from pathlib import Path
from datetime import timedelta
from environ import Env
import os
import sys

# ==================================================
# BASE DIRECTORY
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# ==================================================
# ENVIRONMENT VARIABLES
# ==================================================

env = Env(
    DEBUG=(bool, True)
)

Env.read_env(os.path.join(BASE_DIR, ".env"))

# ==================================================
# SECURITY
# ==================================================

SECRET_KEY = env(
    "SECRET_KEY",
    default="django-insecure-trackflow-dev"
)

DEBUG = env.bool(
    "DEBUG",
    default=True
)

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]

# ==================================================
# APPLICATIONS
# ==================================================

INSTALLED_APPS = [

    # Django Core

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third Party

    'rest_framework',

    'rest_framework_simplejwt',

    'rest_framework_simplejwt.token_blacklist',

    'django_filters',

    'django_fsm',

    # TrackFlow Apps

    'apps.accounts',

    'apps.shipments',

    'apps.tracking',

    'apps.routing',

    'apps.billing',

    'apps.returns',

    'apps.notifications',

    'apps.partners',
]

# ==================================================
# MIDDLEWARE
# ==================================================

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ==================================================
# URLS
# ==================================================

ROOT_URLCONF = 'config.urls'

# ==================================================
# TEMPLATES
# ==================================================

TEMPLATES = [

    {
        'BACKEND':
        'django.template.backends.django.DjangoTemplates',

        'DIRS': [

            BASE_DIR / "templates"

        ],

        'APP_DIRS': True,

        'OPTIONS': {

            'context_processors': [

                'django.template.context_processors.debug',

                'django.template.context_processors.request',

                'django.contrib.auth.context_processors.auth',

                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ==================================================
# WSGI / ASGI
# ==================================================

WSGI_APPLICATION = 'config.wsgi.application'

ASGI_APPLICATION = 'config.asgi.application'

# ==================================================
# DATABASE (POSTGRESQL)
# ==================================================

DATABASES = {

    'default': {

        'ENGINE': env(
            'DB_ENGINE',
            default='django.db.backends.postgresql'
        ),

        'NAME': env(
            'DB_NAME',
            default='trackflow_db'
        ),

        'USER': env(
            'DB_USER',
            default='postgres'
        ),

        'PASSWORD': env(
            'DB_PASSWORD',
            default=''
        ),

        'HOST': env(
            'DB_HOST',
            default='localhost'
        ),

        'PORT': env(
            'DB_PORT',
            default='5432'
        ),
    }
}

# ==================================================
# PASSWORD VALIDATION
# ==================================================

AUTH_PASSWORD_VALIDATORS = [

    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },

    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
    },

    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },

    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ==================================================
# INTERNATIONALIZATION
# ==================================================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True

# ==================================================
# STATIC + MEDIA
# ==================================================

STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"

# ==================================================
# DEFAULT PK
# ==================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================================================
# REST FRAMEWORK
# ==================================================

REST_FRAMEWORK = {

    'DEFAULT_AUTHENTICATION_CLASSES': (

        'rest_framework_simplejwt.authentication.JWTAuthentication',

    ),

    'DEFAULT_PERMISSION_CLASSES': (

        'rest_framework.permissions.IsAuthenticated',

    ),

    'DEFAULT_FILTER_BACKENDS': (

        'django_filters.rest_framework.DjangoFilterBackend',

    ),
}

# ==================================================
# JWT
# ==================================================

SIMPLE_JWT = {

    'ACCESS_TOKEN_LIFETIME':
    timedelta(minutes=60),

    'REFRESH_TOKEN_LIFETIME':
    timedelta(days=1),

    'AUTH_HEADER_TYPES':
    ('Bearer',),

    'AUTH_TOKEN_CLASSES':
    ('rest_framework_simplejwt.tokens.AccessToken',),
}

# ==================================================
# CUSTOM USER
# ==================================================

AUTH_USER_MODEL = 'accounts.CustomUser'

# ==================================================
# CHANNELS + REDIS
# ==================================================

CHANNEL_LAYERS = {

    "default": {

        "BACKEND":
        "channels_redis.core.RedisChannelLayer",

        "CONFIG": {

            "hosts": [

                ("127.0.0.1", 6379)

            ],
        },
    },
}

# ==================================================
# CELERY
# ==================================================

CELERY_BROKER_URL = env(

    "CELERY_BROKER_URL",

    default='redis://127.0.0.1:6379/0'
)

CELERY_RESULT_BACKEND = env(

    "CELERY_RESULT_BACKEND",

    default='redis://127.0.0.1:6379/0'
)

# ==================================================
# STORAGE
# ==================================================

TRACKFLOW_STORAGE_BACKEND = env(

    "TRACKFLOW_STORAGE_BACKEND",

    default='local'
)

TRACKFLOW_ASYNC_LABELS = env.bool(

    "TRACKFLOW_ASYNC_LABELS",

    default=False
)

AWS_STORAGE_BUCKET_NAME = env(

    "AWS_STORAGE_BUCKET_NAME",

    default=""
)

AWS_S3_REGION_NAME = env(

    "AWS_S3_REGION_NAME",

    default="ap-south-1"
)

# ==================================================
# EMAIL
# ==================================================

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

EMAIL_HOST = env(

    "EMAIL_HOST",

    default="smtp.gmail.com"
)

EMAIL_PORT = env.int(

    "EMAIL_PORT",

    default=587
)

EMAIL_HOST_USER = env(

    "EMAIL_HOST_USER",

    default=""
)

EMAIL_HOST_PASSWORD = env(

    "EMAIL_HOST_PASSWORD",

    default=""
)

EMAIL_USE_TLS = env.bool(

    "EMAIL_USE_TLS",

    default=True
)

DEFAULT_FROM_EMAIL = env(

    "DEFAULT_FROM_EMAIL",

    default="noreply@trackflow.com"
)

# ==================================================
# SMS
# ==================================================

SMS_API_URL = env(

    "SMS_API_URL",

    default=""
)

SMS_API_KEY = env(

    "SMS_API_KEY",

    default=""
)

SMS_SENDER_ID = env(

    "SMS_SENDER_ID",

    default=""
)

# ==================================================
# WHATSAPP
# ==================================================

WHATSAPP_API_URL = env(

    "WHATSAPP_API_URL",

    default=""
)

WHATSAPP_TOKEN = env(

    "WHATSAPP_TOKEN",

    default=""
)

# ==================================================
# TEST SETTINGS
# ==================================================

if 'test' in sys.argv:

    CELERY_TASK_ALWAYS_EAGER = True

    CELERY_TASK_EAGER_PROPAGATES = True