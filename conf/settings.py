from pathlib import Path
import os
import sys
import socket
from environs import Env

from django.utils.translation import gettext_lazy as _
import dj_database_url
from rich.logging import RichHandler


env = Env()
env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "apps"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

ENVIRONMENT = env.str("ENVIRONMENT", 'development')

if ENVIRONMENT == 'production':
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=1)

ALLOWED_HOSTS = ["localhost", 
                 "127.0.0.1", 
                 "djs-tnsaman.fandogh.cloud",
                 "takhte-whiteboard.ir",
                 "0233-162-55-176-247.eu.ngrok.io"]


# Application definition

INSTALLED_APPS = [
    # Built-in apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third-party apps
    'debug_toolbar',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'algoliasearch_django',
    'crispy_forms',
    'ckeditor',
    'ckeditor_uploader',
    'channels',
    'channels_redis',
    'seleniumlogin',
    'django_filters',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'drf_yasg',
    'webpush',

    # Local apps
    'users.apps.UsersConfig',
    'homeapp',
    'mainapp',
    'teachers',
    'students',
    'supports',
    'messenger',
    'api',
]

MIDDLEWARE = [
    'compression_middleware.middleware.CompressionMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
]

ROOT_URLCONF = 'conf.urls'
TEMPLATE_DIR = os.path.join(CORE_DIR, "templates")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(TEMPLATE_DIR)],
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
TEMPLATES[0]['OPTIONS']['context_processors'].append("mainapp.context_processors.vapid_key")

ASGI_APPLICATION = 'conf.asgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env.str("DB_NAME", "postgres"),
        'USER': env.str("DB_USER", "saman"),
        'PASSWORD': env.str("DB_PASSWORD", "123456789"),
        'PORT': 5432,
        'HOST': env.str("DB_HOST", "db"),
        'TEST': {
            "NAME": os.path.join(BASE_DIR, "db_test.sqlite3"),
        },
    },
}

db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

AUTH_USER_MODEL = 'users.CustomUser'


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = (('en', _('English')), ('fa', _('Persian')))

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'rich.logging.RichHandler',
            'formatter': 'console'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'console',
            'filename': 'logs/app/app.log'
        }
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
        }
    }
}


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, os.path.join("staticfiles"))
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(CORE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_ID = 1

# Crispy Forms Configuration
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# DjDT confs
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[:-1] + '1' for ip in ips] + ['127.0.0.1', '10.0.2.2']

# Allauth confs
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_ADAPTER = "users.forms.CustomSignUpAdapter"
ACCOUNT_AUTHENTICATION_METHOD = "username"
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_FORMS = {
    'login': 'users.forms.CustomLoginForm',
    'signup': 'users.forms.BaseSignupForm',
    'reset_password': 'users.forms.CustomPasswordResetForm',
    'add_email': 'users.forms.CustomAddEmailForm',
}
LOGIN_REDIRECT_URL = "home:home"
ACCOUNT_SIGNUP_REDIRECT_URL = "supports:create-school"

# Email backend confs
DEFAULT_FROM_EMAIL = "contact@takhte-whiteboard.ir"
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "cp.baseprovider.com"
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 465
DEFAULT_FROM_HOST = EMAIL_HOST_USER
EMAIL_USE_SSL = True

# Admins configuration
ADMINS = [
    ('Saman', 'tnsperuse@gmail.com'),
]

# CKEditor configuration
CKEDITOR_UPLOAD_PATH = 'media/ckeditor/'
CKEDITOR_IMAGE_BACKEND = "ckeditor_uploader.backends.PillowBackend"
CKEDITOR_BROWSE_SHOW_DIRS = False
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar_Basic': [
            ['Source', '-', 'Bold', 'Italic']
        ],
        'toolbar_Customized': [
            {'name': 'document', 'items': ['Templates']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'editing', 'items': ['Find', 'Replace', '-', 'SelectAll']},
            '/',
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl',
                       'Language']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert',
             'items': ['Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley', 
                       'SpecialChar', 'Mathjax', 'PageBreak', 'Iframe']},
            '/',
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize', 'ShowBlocks', 'Preview']},
        ],
        'toolbar': 'Customized',
        'height': 291,
        'width': '100%',
        'toolbarCanCollapse': True,
        'mathJaxLib': '//cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_HTML',
        'extraPlugins': ','.join([
            'mathjax', 
        ]),
    },
}


# Channels
REDIS_HOST = env.str("REDIS_HOST", "redis_server")
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [
                (REDIS_HOST, 6379),
            ],
        },
    },
}

# Algolia search configurations
ALGOLIA_APPLICATION_ID = env.str("ALGOLIA_APPLICATION_ID")
ALGOLIA_API_KEY = env.str("ALGOLIA_API_KEY")
ALGOLIA_SEARCH_KEY = env.str("ALGOLIA_SEARCH_KEY")
ALGOLIA = {
    "AUTO_INDEXING": False,
    "APPLICATION_ID": ALGOLIA_APPLICATION_ID,
    "SEARCH_API_KEY": ALGOLIA_SEARCH_KEY,
    "API_KEY": ALGOLIA_API_KEY,
}

# DRF configurations
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
    ],
}
REST_USE_JWT = True
JWT_AUTH_COOKIE = 'takhteWhiteboard-token'
JWT_AUTH_REFRESH_COOKIE = 'takhteWhiteboard-refresh-token'

# selenium-force-login configurations
SELENIUM_LOGIN_START_PAGE = "/accounts/login/"

# webpush configurations
WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": env.str("VAPID_PUBLIC_KEY"),
    "VAPID_PRIVATE_KEY": env.str("VAPID_PRIVATE_KEY"),
    "VAPID_ADMIN_EMAIL": "contact@takhte-whiteboard.ir",
}
