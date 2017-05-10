import os

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite://')


ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
PAGE_ID = os.environ.get('PAGE_ID')
APP_ID = os.environ.get('APP_ID')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')
SECRET_KEY = os.environ.get('SECRET_KEY')

