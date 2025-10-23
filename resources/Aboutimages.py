import os
import uuid
from datetime import datetime
from flask import request, jsonify
from flask_restful import Resource
from werkzeug.utils import secure_filename
from models import AboutUsImage, db
from supabase import create_client, Client
from dotenv import load_dotenv

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "uploads")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
            file.save(local_path)  # Save locally first

            try:
                with open(local_path, "rb") as f:
                    res = supabase.storage.from_(SUPABASE_BUCKET).upload(
                        f"About_images/{unique_name}", f
                    )

                public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(
                    f"About_images/{unique_name}"
                )

                print(f"✅ Uploaded to Supabase: {public_url}")

            except Exception as e:
                print(f"⚠️ Supabase upload failed: {e}")
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
                with open(local_path, "rb") as f:
                    supabase.storage.from_(SUPABASE_BUCKET).upload(
                        f"About_images/{unique_name}", f
                    )

                public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(
                    f"About_images/{unique_name}"
                )

                # Delete old image from Supabase
                try:
                    supabase.storage.from_(SUPABASE_BUCKET).remove(
                        [f"About_images/{image.filename}"]
                    )
                except Exception as e:
                    print(f"⚠️ Failed to delete old image: {e}")
                    print("🔍 SUPABASE_URL:", SUPABASE_URL)
                    print("🔍 SUPABASE_KEY:", SUPABASE_KEY[:10] if SUPABASE_KEY else None)
                    print("🔍 SUPABASE_BUCKET:", SUPABASE_BUCKET)


                print(f"✅ Updated Supabase image: {public_url}")

            except Exception as e:
                print(f"⚠️ Supabase upload failed: {e}")
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

        try:
            supabase.storage.from_(SUPABASE_BUCKET).remove(
                [f"About_images/{image.filename}"]
            )
            print(f"🗑️ Deleted from Supabase: {image.filename}")
        except Exception as e:
            print(f"⚠️ Supabase delete failed: {e}")

        # Delete local backup
        file_path = os.path.join(UPLOAD_FOLDER, image.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        db.session.delete(image)
        db.session.commit()
        return {"message": "Image deleted successfully"}, 200
