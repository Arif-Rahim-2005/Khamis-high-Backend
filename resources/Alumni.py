from flask import request, jsonify
from flask_restful import Resource
from werkzeug.utils import secure_filename
from models import db, Alumni
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import os
import uuid

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
UPLOAD_FOLDER = os.path.join("uploads", "Alumni")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------------
# 🔹 Alumni Resource
# -------------------------------
class AlumniResource(Resource):
    def get(self, id=None):
        """Get all alumni or a specific one by ID"""
        if id:
            alumni = Alumni.query.get_or_404(id)
            return jsonify({
                "id": alumni.id,
                "name": alumni.name,
                "current_title": alumni.current_title,
                "year_of_completion": alumni.year_of_completion,
                "comment": alumni.comment,
                "image_path": alumni.image_path  # Already a Cloudinary URL
            })

        alumni_list = Alumni.query.all()
        return jsonify({
            "alumni": [
                {
                    "id": a.id,
                    "name": a.name,
                    "current_title": a.current_title,
                    "year_of_completion": a.year_of_completion,
                    "comment": a.comment,
                    "image_path": a.image_path
                } for a in alumni_list
            ]
        })

    def post(self):
        """Add new alumni"""
        name = request.form.get("name")
        current_title = request.form.get("current_title")
        year_of_completion = request.form.get("year_of_completion")
        comment = request.form.get("comment")
        image = request.files.get("image")

        if not name or not comment:
            return {"message": "Name and comment are required."}, 400

        public_url = None
        if image:
            filename = secure_filename(image.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            local_path = os.path.join(UPLOAD_FOLDER, unique_name)
            image.save(local_path)

            try:
                res = cloudinary.uploader.upload(local_path, folder="Alumni")
                public_url = res['secure_url']
                print(f"✅ Uploaded to Cloudinary: {public_url}")
            except Exception as e:
                print(f"⚠️ Cloudinary upload failed: {e}")
                public_url = f"/uploads/Alumni/{unique_name}"

        new_alumni = Alumni(
            name=name,
            current_title=current_title,
            year_of_completion=year_of_completion,
            comment=comment,
            image_path=public_url
        )
        db.session.add(new_alumni)
        db.session.commit()

        return {"message": "Alumni added successfully!"}, 201

    def put(self, id):
        """Edit existing alumni"""
        alumni = Alumni.query.get_or_404(id)

        alumni.name = request.form.get("name", alumni.name)
        alumni.current_title = request.form.get("current_title", alumni.current_title)
        alumni.year_of_completion = request.form.get("year_of_completion", alumni.year_of_completion)
        alumni.comment = request.form.get("comment", alumni.comment)

        image = request.files.get("image")
        if image:
            filename = secure_filename(image.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            local_path = os.path.join(UPLOAD_FOLDER, unique_name)
            image.save(local_path)

            try:
                res = cloudinary.uploader.upload(local_path, folder="Alumni")
                public_url = res['secure_url']
                print(f"✅ Updated Cloudinary image: {public_url}")
                alumni.image_path = public_url
            except Exception as e:
                print(f"⚠️ Cloudinary upload failed: {e}")

        db.session.commit()
        return {"message": "Alumni updated successfully!"}, 200

    def delete(self, id):
        """Delete alumni"""
        alumni = Alumni.query.get_or_404(id)

        # Delete from Cloudinary
        if alumni.image_path:
            try:
                filename_with_ext = alumni.image_path.split('/')[-1]
                public_id = filename_with_ext.rsplit('.', 1)[0]
                public_id = f"Alumni/{public_id}"
                cloudinary.uploader.destroy(public_id)
                print(f"🗑️ Deleted from Cloudinary: {public_id}")
            except Exception as e:
                print(f"⚠️ Cloudinary delete failed: {e}")

        db.session.delete(alumni)
        db.session.commit()
        return {"message": "Alumni deleted successfully!"}, 200