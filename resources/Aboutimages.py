import os
import uuid
from datetime import datetime
from flask import request, jsonify
from flask_restful import Resource
from werkzeug.utils import secure_filename
from models import AboutUsImage, db
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# -------------------------------
# Local fallback storage (for dev)
# -------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'About_images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# -------------------------------
# 🔹 1. Get all images
# -------------------------------
class AboutUsImages(Resource):
    def get(self):
        images = AboutUsImage.query.all()
        data = [
            {
                "id": img.id,
                "filename": img.filename,
                "filepath": img.filepath,
                "uploaded_at": img.uploaded_at,
                "updated_at": img.updated_at
            }
            for img in images
        ]
        return jsonify({"images": data})


# -------------------------------
# 🔹 2. Upload new image
# -------------------------------
class UploadAboutImage(Resource):
    def post(self):
        if 'file' not in request.files:
            return {"message": "No file part"}, 400

        file = request.files['file']

        if file.filename == '':
            return {"message": "No selected file"}, 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            local_path = os.path.join(UPLOAD_FOLDER, unique_name)
            file.save(local_path)

            try:
                res = cloudinary.uploader.upload(local_path, folder="About_images")
                public_url = res['secure_url']
                print(f"✅ Uploaded to Cloudinary: {public_url}")
            except Exception as e:
                print(f"⚠️ Cloudinary upload failed: {e}")
                public_url = f"/uploads/About_images/{unique_name}"

            new_img = AboutUsImage(filename=unique_name, filepath=public_url)
            db.session.add(new_img)
            db.session.commit()

            return {
                "message": "Image uploaded successfully",
                "url": public_url
            }, 201

        return {"message": "Invalid file type"}, 400

# -------------------------------
# 🔹 3. Update existing image
# -------------------------------
class UpdateAboutImage(Resource):
    def put(self, image_id):
        image = AboutUsImage.query.get(image_id)
        if not image:
            return {"message": "Image not found"}, 404

        if 'file' not in request.files:
            return {"message": "No file provided"}, 400

        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            local_path = os.path.join(UPLOAD_FOLDER, unique_name)
            file.save(local_path)

            try:
                res = cloudinary.uploader.upload(local_path, folder="About_images")
                public_url = res['secure_url']
                print(f"✅ Updated Cloudinary image: {public_url}")
            except Exception as e:
                print(f"⚠️ Cloudinary upload failed: {e}")
                public_url = f"/uploads/About_images/{unique_name}"

            image.filename = unique_name
            image.filepath = public_url
            image.updated_at = datetime.utcnow()
            db.session.commit()

            return {"message": "Image updated successfully", "url": public_url}, 200

        return {"message": "Invalid file type"}, 400


# -------------------------------
# 🔹 4. Delete image
# -------------------------------
class DeleteAboutImage(Resource):
    def delete(self, image_id):
        image = AboutUsImage.query.get(image_id)
        if not image:
            return {"message": "Image not found"}, 404

        # Delete from Cloudinary
        try:
            filename_with_ext = image.filepath.split('/')[-1]
            public_id = filename_with_ext.rsplit('.', 1)[0]
            public_id = f"About_images/{public_id}"

            cloudinary.uploader.destroy(public_id)
            print(f"🗑️ Deleted from Cloudinary: {public_id}")
        except Exception as e:
            print(f"⚠️ Cloudinary delete failed: {e}")

        # Delete local backup
        file_path = os.path.join(UPLOAD_FOLDER, image.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        db.session.delete(image)
        db.session.commit()
        return {"message": "Image deleted successfully"}, 200
