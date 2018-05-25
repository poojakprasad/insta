from flask import Flask
from flask_cors import CORS

app = Flask('app_insta',
            static_folder='./static',
            static_url_path='',
            template_folder='./templates')
CORS(app)
app.secret_key = 'insta_key'

from app_insta import views, api
