from flask import *

from Forms.forms import forms_bp
from User.User_Profile.user import user_profile_bp
from User.User_Mail.user_mail import user_mail_bp
from api.api import users_api_bp
from Admin.admins import admin_bp

import os

app = Flask(__name__)

if app.config['ENV'] == 'production':
    app.config.from_object('config.prod_config')
else:
    app.config.from_object('config.dev_config')

app.config['SECRET_KEY'] = 'bdksjbgbnfgbbsaghroeihgiknv'


app.register_blueprint(forms_bp)
app.register_blueprint(user_profile_bp)
app.register_blueprint(user_mail_bp)
app.register_blueprint(users_api_bp, url_prefix='/api')
app.register_blueprint(admin_bp)


def getApp():
    return app


if __name__ == "__main__":
    app.run(debug=True)
