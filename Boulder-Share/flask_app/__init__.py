from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv() 
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

base_dir = os.path.abspath(os.path.dirname(__file__))

uploads_folder = os.path.join(base_dir, 'static', 'uploads')

app.config['UPLOAD_FOLDER'] = uploads_folder
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
