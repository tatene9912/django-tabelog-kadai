"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 5.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-4y33do6^h2kn94oigqp!i8ki+xwee%%-tvd^#i5b2_@q*j$ez)'


# Application definition
import os

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',
    'tabelog.apps.TabelogConfig',
    'import_export',
    'accounts',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'django_bootstrap5',
    'widget_tweaks',
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', #デフォルトの認証基盤 
    'allauth.account.auth_backends.AuthenticationBackend' # メールアドレスとパスワードの両方を用いて認証するために必要
)

LOGIN_URL = 'account_login' # ログインURLの設定
LOGIN_REDIRECT_URL = 'tabelog:top' # ログイン後のリダイレクト先
ACCOUNT_LOGOUT_REDIRECT_URL = 'account_login' #　ログアウト後のリダイレクト先

AUTH_USER_MODEL = "accounts.User" # カスタムユーザーを認証用ユーザーとして登録
# Allauthの設定
ACCOUNT_USER_MODEL_USERNAME_FIELD = None  # usernameフィールドを無効化
ACCOUNT_USERNAME_REQUIRED = False  # usernameを不要にする
ACCOUNT_EMAIL_REQUIRED = True  # emailを必須にする
ACCOUNT_AUTHENTICATION_METHOD = 'email'  # emailで認証する
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True  # パスワード確認フィールドを使用する場合
ACCOUNT_EMAIL_VERIFICATION = 'mandatory' # メール検証を必須とする

ACCOUNT_LOGOUT_ON_GET = True

ACCOUNT_FORMS = {
    'signup': 'accounts.forms.CustomSignupForm',
}


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' 
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 't.atene0l4o1v2e@gmail.com'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER # send_mailのfromがNoneの場合自動で入る。
EMAIL_HOST_PASSWORD = ''

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'mysite.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


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


LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
ALLOWED_HOSTS = ['127.0.0.1' ,'herokuapp.com']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# STRIPE 追加
STRIPE_PUBLIC_KEY = 'pk_test_51PyCjbDDYJcRPnIUQOk8J2BIOrWfaWq5YaKl80rmRW8ZLA8MkngSsKxgJuhHYGCuVZfQYIrNxPCqqu3HXhFuK87C00wWxgm0hf'
STRIPE_SECRET_KEY = ''
STRIPE_PRICE_ID = 'price_1PyCqhDDYJcRPnIUf7D4PyiK'
STRIPE_ENDPOINT_SECRET = ''

CLOUDINARY_STORAGE  = {
    'CLOUD_NAME':'hoep8dpt4',
    'API_KEY': '785511999933492',
    'API_SECRET': ''
}

DEBUG = False

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "%(asctime)s [%(levelname)s] %(message)s"}},
    "handlers": {
        "info": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "warning": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "stream": "ext://sys.stderr",
        },
        "error": {
            "level": "ERROR",
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "stream": "ext://sys.stderr",
        },
    },
    "root": {
        "handlers": ["info", "warning", "error"],
        "level": "INFO",
    },
}


import dj_database_url
db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)

db_from_env = dj_database_url.config(conn_max_age=600, ssl_require=True)
DATABASES['default'].update(db_from_env)


if not DEBUG:
    SECRET_KEY = '9h2=518scv!cut0s70!2xa=q8y1h3@6n&xroxa)fq_t#$5(686'   
    import django_heroku
    django_heroku.settings(locals())
