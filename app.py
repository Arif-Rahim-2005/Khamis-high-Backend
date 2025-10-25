import os
from dotenv import load_dotenv
# from supabase import create_client, Client
from flask import Flask, jsonify, send_from_directory
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
from resources.fee import FeeStructureResource
from resources.Aboutimages import AboutUsImages, UploadAboutImage, UpdateAboutImage, DeleteAboutImage
from resources.Alumni import AlumniResource
import cloudinary
import cloudinary.uploader
load_dotenv()
print("DATABASE_URL ->", os.getenv("DATABASE_URL"))

cloudinary.config(
  cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
  api_key=os.getenv("CLOUDINARY_API_KEY"),
  api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# ---------------------------
# Load environment variables
# ---------------------------

# Initialize app
app = Flask(__name__)
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------
# CONFIGS
# ---------------------------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

UPLOAD_FOLDER = '/home/arifrahim/Projects/Khamishigh/Khamis-high-Backend/uploads'


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

# 'postgresql://neondb_owner:npg_KAflHrdX25ao@ep-raspy-salad-ag6zgnpz-pooler.c-2.eu-central-1.aws.neon.tech/Khamisdb?sslmode=require&channel_binding=require'
# 
# 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')

# ---------------------------
# EXTENSIONS
# ---------------------------
CORS(app)
# CORS(app, resources={
#     r"/*": {
#         "origins": ["http://localhost:5174", "http://127.0.0.1:5174"],
#         "supports_credentials": True,
#         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#         "allow_headers": ["Authorization", "Content-Type"]
#     }
# })
# @app.before_request
# def handle_preflight():
#     if request.method == "OPTIONS":
#         response = app.make_default_options_response()
#         headers = response.headers

#         # Manually allow the frontend origin + headers
#         headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
#         headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
#         headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
#         headers['Access-Control-Allow-Credentials'] = 'true'
#         return response

api = Api(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
db.init_app(app)

# ---------------------------
# ROUTES
# ---------------------------
@app.route('/')
def home():
    return jsonify(message="Welcome to the Khamis High Backend API")

# ✅ Serve uploaded files
@app.route('/uploads/<path:filename>')
def serve_uploaded_file(filename):
    """Serve uploaded images and files safely."""
    return send_from_directory(UPLOAD_FOLDER, filename)


# ✅ RESTful endpoints
api.add_resource(SystemResource, '/systems', '/systems/<int:system_id>')
api.add_resource(DepartmentResource, '/departments', '/departments/<int:department_id>')
api.add_resource(TrackResource, '/tracks', '/tracks/<int:track_id>')
api.add_resource(SubjectResource, '/subjects', '/subjects/<int:subject_id>')
api.add_resource(SignupResource, "/signup")
api.add_resource(LogInResource, "/login")
api.add_resource(AdminResource, "/me")
api.add_resource(UserResource, "/users", "/users/<int:user_id>")
api.add_resource(ClubsResource, "/clubs", "/clubs/<int:club_id>")
api.add_resource(SubjectSelectionResource, "/subject-selections")
api.add_resource(SubjectSelectionByIdResource, "/subject-selections/<int:selection_id>")
api.add_resource(FeeStructureResource, "/fee-structure")
# api.add_resource(ServeFeeStructureFile, "/fee-structure-file/<string:filename>")
api.add_resource(AboutUsImages, '/about/images')
api.add_resource(UploadAboutImage, '/about/upload')
api.add_resource(UpdateAboutImage, '/about/image/<int:image_id>')
api.add_resource(DeleteAboutImage, '/about/image/<int:image_id>')
api.add_resource(AlumniResource, "/alumni", "/alumni/<int:id>")
# register_upload_route(app)
# ---------------------------
# MAIN
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
