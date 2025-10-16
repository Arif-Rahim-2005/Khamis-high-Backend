import os
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
from resources.users import SignupResource, LogInResource, UserResource, AdminResource
from resources.subjectsresource import SubjectResource
from resources.clubs import ClubsResource
from resources.subjectselection import SubjectSelectionResource, SubjectSelectionByIdResource
from resources.fee import FeeStructureResource, ServeFeeStructureFile
from resources.Aboutimages import AboutUsImages, UploadAboutImage, UpdateAboutImage, DeleteAboutImage






# Load environment variables
load_dotenv()

# Initialize app
app = Flask(__name__)

# --- CONFIGS ---
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
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
api.add_resource(AdminResource, "/me")
api.add_resource(UserResource, "/users", "/users/<int:user_id>")

# ⚠️ FIX: Add missing forward slash in routes below
api.add_resource(ClubsResource, "/clubs", "/clubs/<int:club_id>")

api.add_resource(SubjectSelectionResource, "/subject-selections")
api.add_resource(SubjectSelectionByIdResource, "/subject-selections/<int:selection_id>")
api.add_resource(FeeStructureResource, "/fee-structure")
api.add_resource(ServeFeeStructureFile, "/fee-structure-file/<string:filename>")



api.add_resource(AboutUsImages, '/about/images')
api.add_resource(UploadAboutImage, '/about/upload')
api.add_resource(UpdateAboutImage, '/about/image/<int:image_id>')
api.add_resource(DeleteAboutImage, '/about/image/<int:image_id>')

# --- MAIN ---
if __name__ == '__main__':
    app.run(port=5000, debug=True)
