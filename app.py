import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restful import Api
from models import db
from resources.systemresource import SystemResource
from resources.departments import DepartmentResource
from resources.tracks import TrackResource
from resources.users import SignupResource, LogInResource, UserResource
from resources.subjectsresource import SubjectResource
from resources.clubs import ClubsResource

# Load environment variables
load_dotenv()

# Initialize app
app = Flask(__name__)

# --- CONFIGS ---
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')

# --- EXTENSIONS ---
CORS(app)
api = Api(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
db.init_app(app)

# --- ROUTES ---
@app.route('/')
def home():
    return jsonify(message="Welcome to the Khamis High Backend API")

# ✅ RESTful endpoints
api.add_resource(SystemResource,
    '/systems',
    '/systems/<int:system_id>'
)

api.add_resource(DepartmentResource,
    '/departments',
    '/departments/<int:department_id>'
)

api.add_resource(TrackResource,
    '/tracks',
    '/tracks/<int:track_id>'
)

api.add_resource(SubjectResource,
    '/subjects',
    '/subjects/<int:subject_id>'
)

api.add_resource(SignupResource, "/signup")
api.add_resource(LogInResource, "/login")
api.add_resource(UserResource, "/users", "/users/<int:user_id>")

# ⚠️ FIX: Add missing forward slash in routes below
api.add_resource(ClubsResource, "/clubs", "/clubs/<int:club_id>")

# --- MAIN ---
if __name__ == '__main__':
    app.run(port=5000, debug=True)
