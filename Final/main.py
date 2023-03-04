import os
from aenum import unique
from flask import Flask
from flask_restful import Resource, Api
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db
from application.models import new_user, tracker_data
from numpy import False_, unicode_

import matplotlib as plt

app = None
api = None

def create_app():
    app = Flask(__name__, template_folder='templates')
    if os.getenv('ENV', "developement") == "production":
        raise Exception("Currently no production config is setup")
    else:
        print("starting local developement")
        app.config.from_object(LocalDevelopmentConfig)
    app.secret_key = "thisisasecretkey"
    db.init_app(app)
    api = Api(app)
    app.app_context().push()
    return app, api

app, api = create_app()

from application.controllers import *

if __name__ == '__main__':
    # Run the flask app
    app.run(host='0.0.0.0', debug=True, port=5000)