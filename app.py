from flask import Flask
from models import db, init_db
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
database_uri = os.getenv('DATABASE_URI', f'sqlite:///{os.path.join(basedir, "hospital.db")}')

app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'


db.init_app(app)

with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])

