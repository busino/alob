'''
Alob Project
2016 -2018
Author(s): R.Walker

'''
import os

#
# Alob Specific Settings
#
#

DEPLOY_TYPE = 'production'#'production'# 'dev'

SEARCH_RADIUS = 0.17
PRESELECT_SEARCH_RADIUS = 0.25

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOG_PATH = os.path.abspath(os.path.join(BASE_DIR, '..'))

if DEPLOY_TYPE == 'production':
    MEDIA_ROOT = os.path.join('/src/data/media')
    LOG_PATH = '/log/'

MEDIA_URL = '/media/'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'tudscz@3sih!+isw_#fl9#v0e^b5*k_&-&5-3t'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['159.100.250.81', 'localhost', '127.0.0.1', '159.100.247.204']

# Application definition
INSTALLED_APPS = [
    'image.apps.ImageConfig',
    'pair.apps.PairConfig',
    'prediction.apps.PredictionConfig',
    'contrib',
    'bootstrap3',
    'django_filters',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    #'debug_toolbar',
]

MIDDLEWARE_CLASSES = [
    #'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',#needed by admin
    #'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'alob_django.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',# needed to highlight active links
                'django.contrib.auth.context_processors.auth',# used for admin
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django_settings_export.settings_export',
            ],
        },
    },
]

WSGI_APPLICATION = 'alob_django.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'alob',                      # Or path to database file if using sqlite3.
        'USER': 'alob',                     # Not used with sqlite3.
        'PASSWORD': 'alob',                  # Not used with sqlite3.
        'HOST': {'production': 'db', 'dev': ''}.get(DEPLOY_TYPE, 'db'),
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    },
    'default_sqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'alob.sqlite'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators


AUTH_PASSWORD_VALIDATORS = []
# 
# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

#LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'en-us'
#TIME_ZONE = 'Europe/Zurich'
#USE_I18N = True
#USE_L10N = True
USE_TZ = False
#FORMAT_MODULE_PATH = 'contrib.formats'
DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i:s'
TIME_FORMAT = 'H:i:s'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATIC_URL = '/static/'

# Settings Export
###################################
BOKEH_DIR = 'vendor/bokeh_1.4.0'
BOOTSTRAP_DIR = 'vendor/bootstrap-3.3.7'
JQUERY = 'vendor/js/jquery-3.2.0.min.js'
JQUERY_TABLESORTER = 'vendor/js/jquery.tablesorter.min.js'
FONT_AWESOME_DIR = 'vendor/font-awesome-4.7.0'

SETTINGS_EXPORT = [
    'BOKEH_DIR',
    'BOOTSTRAP_DIR',
    'JQUERY',
    'JQUERY_TABLESORTER',
    'FONT_AWESOME_DIR',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
         },
        'logfile': {
            'format': '%(levelname)-8s %(asctime)s %(module)-10s %(message)s'
        }
    },           
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024*1024*20, # 20MB
            'filename': os.path.join(LOG_PATH, 'data_processing_2.log'),
            'formatter': 'logfile',
        },
    },
    'loggers': {
        'django.utils.autoreload': {
           'level': 'INFO',
        },
        'django': {
            'handlers': ['console', 'logfile'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'django.db.backends': {
            'propagate': False,
            'level':'ERROR',
        },
        'alob': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
    },
}