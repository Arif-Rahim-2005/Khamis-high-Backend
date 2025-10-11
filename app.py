import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restful import Api
from models import db, User, System, Department, Track, Subject, ClubandSociety

load_dotenv()
app = Flask(__name__)
CORS(app)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///school.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')
jwt = JWTManager(app)
migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def home():
    return jsonify(message="Welcome to the Khamis High Backend API")




if __name__ == '__main__':
    app.run(port=5000)

