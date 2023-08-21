import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

login = LoginManager(app)

login.login_view = 'login'
login.login_message = 'Hey, you need to be logged in to do that!'
login.login_message_category = 'info'

from app.models import User

@login.user_loader
def load_user(user_id):
    return User.get_user(user_id)

from app.blueprints.api import api
app.register_blueprint(api)

from app import routes, models
