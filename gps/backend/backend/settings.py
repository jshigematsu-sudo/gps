from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-iz$win7qdn!zx%69c0lixo8k7x9@20h2@q=2oyn3ma*8&2x*ez'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# 許可するホスト
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "gps.iluke.co.jp",
    "0.0.0.0",
    "192.168.3.8",
    "192.168.0.150",
    ".ngrok-free.app",
]

ACCOUNT_LOGIN_METHODS = {"username"}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'channels',
    'corsheaders',
    'dj_rest_auth',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'allauth',
    'allauth.account',
    "allauth.socialaccount",

    'accounts.apps.AccountsConfig',
    'trail_map.apps.TrailMapConfig',
    'current_meet_locations.apps.CurrentMeetLocationsConfig',
    'current_member_positions.apps.CurrentMemberPositionsConfig'
]

CORS_ALLOW_CREDENTIALS = True
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

ASGI_APPLICATION = 'backend.asgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'private_trail_map',
        'USER': 'postgres',
        'PASSWORD': 'jshigematsu',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.CustomUser'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT認証を追加
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # 認証ユーザーのみ許可
    ],
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),  # アクセストークンの有効期限 (30分)
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),     # リフレッシュトークンの有効期限 (7日)
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# CORS設定
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://192.168.0.150:5173",
    "http://192.168.3.8:5173",
    "https://gps.iluke.co.jp",
    # "https://33e2-210-203-214-90.ngrok-free.app",
]

# 認証情報を含むリクエストを許可
CORS_ALLOW_CREDENTIALS = True

# CSRF設定
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://192.168.0.150:5173",
    "http://192.168.3.8:5173",
    "https://gps.iluke.co.jp",
    # "https://33e2-210-203-214-90.ngrok-free.app",
]

# Django のセッション管理設定（認証が必要な場合）
SESSION_COOKIE_SAMESITE = None
SESSION_COOKIE_SECURE = True  # HTTPSを使う場合
CSRF_COOKIE_SECURE = True  # HTTPSを使う場合
CSRF_COOKIE_SAMESITE = None  # 認証時に重要

# メール認証を不要にする
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_USERNAME_REQUIRED = True

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",  # 本番環境ではRedis推奨
    },
}