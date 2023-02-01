from os import environ, path, getcwd
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

load_dotenv(path.join(getcwd(), ".env"))

SECRET_KEY = environ.get('SECRET_KRY')
AWS_ACCESS_KEY_ID = environ.get('AWS_ACCESS_KEY_ID')
SECRET_ACCESS_KEY = environ.get('SECRET_ACCESS_KEY')

db = SQLAlchemy()
