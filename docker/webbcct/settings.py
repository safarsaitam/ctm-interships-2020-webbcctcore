#Utilities' Imports
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.figure import Figure
# from matplotlib.backends.backend_agg import FigureCanvasAgg
# from matplotlib.backends.backend_svg import FigureCanvas
# import matplotlib as mpl
# import mpld3
# from mpld3 import plugins, utils
# import matplotlib.path as mpath
# import matplotlib.patches as mpatches
# from django.http import HttpResponse
# from django.shortcuts import render
# import cv2
# import io
# import platform
# #Keras
# import keras
# from keras import backend as K
# from keras.models import Sequential, Model, load_model
# from keras.layers import Dense
# from keras.layers import Input, Conv2D, MaxPooling2D, Conv2DTranspose, multiply, concatenate, Dense, Flatten, Dropout, Lambda
# from keras.applications import VGG16
# from keras.applications.vgg16 import preprocess_input
# from keras.callbacks import ModelCheckpoint
# from keras import losses
# from keras.applications.vgg16 import preprocess_input


"""
Django settings for webbcct project.

Generated by 'django-admin startproject' using Django 2.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import json

with open('webbcct_config.json') as config_file:
	config = json.load(config_file)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['194.117.29.112', 'medicalresearch.inescporto.pt','localhost','127.0.0.1','0.0.0.0']


# Application definition

INSTALLED_APPS = [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.twitter',
    'mathfilters',
    'django.contrib.sites',
    'crispy_forms',
    'djongo',
    'users.apps.UsersConfig',
    'bcctapp.apps.BcctappConfig',
    'cinderella.apps.CinderellaConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'webbcct.urls'

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

WSGI_APPLICATION = 'webbcct.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# TODO: Mongo DB
"""
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'webbcct',
        # 'HOST': 'mongo', Docker Only
        'HOST':'127.0.0.1',
        'USER': 'breastgroup',
        'PASSWORD': 'inesctec2020',
        'PORT': 27017
    }
}
"""

# Debugg SQLite3
# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

CRISPY_TEMPLATE_PACK= 'bootstrap4'

LOGIN_REDIRECT_URL = 'bcctapp-home'
LOGIN_URL = 'login'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = config.get('EMAIL_PASS')

#MODEL_PATH = '/home/tiagogoncalves/django-app-webbcct.core/utils/15jan2019_14_30.hdf5'
#MODEL = load_model(MODEL_PATH)

AUTHENTICATION_BACKENDS = (

    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',

)

SOCIAL_AUTH_FACEBOOK_KEY = 1041718206160815
SOCIAL_AUTH_FACEBOOK_SECRET = 'f5128dbe5eef75674f3feb36a541a4d8'

SOCIAL_AUTH_TWITTER_KEY = 'LoCkTAuhfF5AmxubHIMBMZt4Y'
SOCIAL_AUTH_TWITTER_SECRET = '9TBjYmZP5vz2zsHWVTyPy65yTlqwEUXhcv1QoWXEUepIopQ5HU'

SITE_ID = 1