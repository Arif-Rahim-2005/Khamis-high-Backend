# import os
# import uuid
# from datetime import datetime
# from flask import request, jsonify
# from flask_restful import Resource
# from werkzeug.utils import secure_filename
# from models import AboutUsImage, db

# # --- Path setup ---
# BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'About_images')
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# # -------------------------------
# # 🔹 1. Get all images
# # -------------------------------
# class AboutUsImages(Resource):
#     def get(self):
#         images = AboutUsImage.query.all()
#         data = [
#             {
#                 "id": img.id,
#                 "filename": img.filename,
#                 "filepath": f"/uploads/About_images/{os.path.basename(img.filepath)}",
#                 "uploaded_at": img.uploaded_at,
#                 "updated_at": img.updated_at
#             }
#             for img in images
#         ]
#         return jsonify({"images": data})


# # -------------------------------
# # 🔹 2. Upload new image
# # -------------------------------
# class UploadAboutImage(Resource):
#     def post(self):
#         if 'file' not in request.files:
#             return {"message": "No file part"}, 400

#         file = request.files['file']

#         if file.filename == '':
#             return {"message": "No selected file"}, 400

#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             unique_name = f"{uuid.uuid4().hex}_{filename}"
#             file_path = os.path.join(UPLOAD_FOLDER, unique_name)
#             file.save(file_path)

#             new_img = AboutUsImage(
#                 filename=unique_name,
#                 filepath=file_path
#             )
#             db.session.add(new_img)
#             db.session.commit()

#             return {"message": "Image uploaded successfully"}, 201

#         return {"message": "Invalid file type"}, 400


# # -------------------------------
# # 🔹 3. Update existing image
# # -------------------------------
# class UpdateAboutImage(Resource):
#     def put(self, image_id):
#         image = AboutUsImage.query.get(image_id)
#         if not image:
#             return {"message": "Image not found"}, 404

#         if 'file' not in request.files:
#             return {"message": "No file provided"}, 400

#         file = request.files['file']

#         if file and allowed_file(file.filename):
#             # delete old file
#             if os.path.exists(image.filepath):
#                 os.remove(image.filepath)

#             filename = secure_filename(file.filename)
#             unique_name = f"{uuid.uuid4().hex}_{filename}"
#             file_path = os.path.join(UPLOAD_FOLDER, unique_name)
#             file.save(file_path)

#             image.filename = unique_name
#             image.filepath = file_path
#             image.updated_at = datetime.utcnow()
#             db.session.commit()

#             return {"message": "Image updated successfully"}, 200

#         return {"message": "Invalid file type"}, 400


# # -------------------------------
# # 🔹 4. Delete image
# # -------------------------------
# class DeleteAboutImage(Resource):
#     def delete(self, image_id):
#         image = AboutUsImage.query.get(image_id)
#         if not image:
#             return {"message": "Image not found"}, 404

#         if os.path.exists(image.filepath):
#             os.remove(image.filepath)

#         db.session.delete(image)
#         db.session.commit()
#         return {"message": "Image deleted successfully"}, 200
import os
import uuid
from datetime import datetime
from flask import request, jsonify
from flask_restful import Resource
from werkzeug.utils import secure_filename
from models import AboutUsImage, db

# --- Path setup ---
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
                "filepath": f"/uploads/{img.filepath}",  # ✅ Serve via Flask route
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

            # Save file to the uploads folder
            file_path = os.path.join(UPLOAD_FOLDER, unique_name)
            file.save(file_path)

            # ✅ Store only relative path in DB
            relative_path = f"About_images/{unique_name}"

            new_img = AboutUsImage(
                filename=unique_name,
                filepath=relative_path
            )
            db.session.add(new_img)
            db.session.commit()

            return {"message": "Image uploaded successfully"}, 201

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
            # Delete old file
            old_file_path = os.path.join(BASE_DIR, 'uploads', image.filepath)
            if os.path.exists(old_file_path):
                os.remove(old_file_path)

            filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"

            # Save new file
            file_path = os.path.join(UPLOAD_FOLDER, unique_name)
            file.save(file_path)

            # ✅ Update DB with relative path
            relative_path = f"About_images/{unique_name}"

            image.filename = unique_name
            image.filepath = relative_path
            image.updated_at = datetime.utcnow()

            db.session.commit()

            return {"message": "Image updated successfully"}, 200

        return {"message": "Invalid file type"}, 400


# -------------------------------
# 🔹 4. Delete image
# -------------------------------
class DeleteAboutImage(Resource):
    def delete(self, image_id):
        image = AboutUsImage.query.get(image_id)
        if not image:
            return {"message": "Image not found"}, 404

        # Delete actual file
        file_path = os.path.join(BASE_DIR, 'uploads', image.filepath)
        if os.path.exists(file_path):
            os.remove(file_path)

        db.session.delete(image)
        db.session.commit()
        return {"message": "Image deleted successfully"}, 200
