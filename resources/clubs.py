# import os
# from flask import request, current_app as app, url_for
# from flask_restful import Resource, reqparse
# from werkzeug.utils import secure_filename
# from models import ClubandSociety, db

# # Folder where club images will be stored
# UPLOAD_FOLDER = os.path.join("uploads", "Clubs")
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# class ClubsResource(Resource):
#     parser = reqparse.RequestParser()
#     parser.add_argument('name', type=str, required=True, help='Name is required')
#     parser.add_argument('description', type=str)

#     def get(self, club_id=None):
#         if club_id:
#             club = ClubandSociety.query.get(club_id)
#             if not club:
#                 return {'message': 'Club not found'}, 404

#             return {
#                 'id': club.id,
#                 'name': club.name,
#                 'description': club.description,
#                 'image_path': f"/uploads/Clubs/{club.image_path}" if club.image_path else None,
#                 'created_at': club.created_at.isoformat()
#             }, 200

#         # Get all clubs
#         clubs = ClubandSociety.query.all()
#         return [{
#             'id': c.id,
#             'name': c.name,
#             'description': c.description,
#             'image_path': f"/uploads/Clubs/{c.image_path}" if c.image_path else None,
#             'created_at': c.created_at.isoformat()
#         } for c in clubs], 200


#     def post(self):
#         name = request.form.get('name')
#         description = request.form.get('description', '')
#         image = request.files.get('image')

#         # check for existing club
#         existing = ClubandSociety.query.filter_by(name=name).first()
#         if existing:
#             return {'message': 'Club already exists'}, 400

#         # handle image upload
#         image_filename = None
#         if image:
#             filename = secure_filename(image.filename)
#             image.save(os.path.join(UPLOAD_FOLDER, filename))
#             image_filename = filename

#         new_club = ClubandSociety(
#             name=name,
#             description=description,
#             image_path=image_filename
#         )

#         db.session.add(new_club)
#         try:
#             db.session.commit()
#             return {
#                 'message': 'Club created successfully',
#                 'club': {
#                     'id': new_club.id,
#                     'name': new_club.name,
#                     'description': new_club.description,
#                     'image_path':f"/uploads/Clubs/{new_club.image_path}" if new_club.image_path else None,
#                     'created_at': new_club.created_at.isoformat()
#                 }
#             }, 201
#         except Exception as e:
#             db.session.rollback()
#             return {'message': 'Error creating club', 'error': str(e)}, 500


#     def patch(self, club_id):
#         club = ClubandSociety.query.get(club_id)
#         if not club:
#             return {'message': 'Club not found'}, 404

#         data = request.form
#         image = request.files.get('image')

#         club.name = data.get('name', club.name)
#         club.description = data.get('description', club.description)

#         # handle image update
#         if image:
#             filename = secure_filename(image.filename)
#             image.save(os.path.join(UPLOAD_FOLDER, filename))
#             club.image_path = filename

#         try:
#             db.session.commit()
#             return {
#                 'message': 'Club updated successfully',
#                 'club': {
#                     'id': club.id,
#                     'name': club.name,
#                     'description': club.description,
#                     'image_path': f"/uploads/Clubs/{club.image_path}" if club.image_path else None,
#                     'created_at': club.created_at.isoformat()
#                 }
#             }, 200
#         except Exception as e:
#             db.session.rollback()
#             return {'message': 'Error updating club', 'error': str(e)}, 500

#     def delete(self, club_id):
#         club = ClubandSociety.query.get(club_id)
#         if not club:
#             return {'message': 'Club not found'}, 404
#         if club.image_path:
#             try:
#                 os.remove(os.path.join(UPLOAD_FOLDER, club.image_path))
#             except FileNotFoundError:
#                 pass


#         db.session.delete(club)
#         try:
#             db.session.commit()
#             return {'message': 'Club deleted successfully'}, 200
#         except Exception as e:
#             db.session.rollback()
#             return {'message': 'Error deleting club', 'error': str(e)}, 500
import os
import uuid
from flask import request
from flask_restful import Resource, reqparse
from werkzeug.utils import secure_filename
from models import ClubandSociety, db
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
UPLOAD_FOLDER = os.path.join("uploads", "Clubs")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------------
# 🔹 Clubs Resource
# -------------------------------
class ClubsResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help='Name is required')
    parser.add_argument('description', type=str)

    def get(self, club_id=None):
        if club_id:
            club = ClubandSociety.query.get(club_id)
            if not club:
                return {'message': 'Club not found'}, 404

            return {
                'id': club.id,
                'name': club.name,
                'description': club.description,
                'image_path': club.image_path,
                'created_at': club.created_at.isoformat()
            }, 200

        clubs = ClubandSociety.query.all()
        return [{
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'image_path': c.image_path,
            'created_at': c.created_at.isoformat()
        } for c in clubs], 200

    def post(self):
        name = request.form.get('name')
        description = request.form.get('description', '')
        image = request.files.get('image')

        existing = ClubandSociety.query.filter_by(name=name).first()
        if existing:
            return {'message': 'Club already exists'}, 400

        public_url = None
        if image:
            filename = secure_filename(image.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            local_path = os.path.join(UPLOAD_FOLDER, unique_name)
            image.save(local_path)

            try:
                res = cloudinary.uploader.upload(local_path, folder="Clubs")
                public_url = res['secure_url']
                print(f"✅ Uploaded to Cloudinary: {public_url}")
            except Exception as e:
                print(f"⚠️ Cloudinary upload failed: {e}")
                public_url = f"/uploads/Clubs/{unique_name}"

        new_club = ClubandSociety(
            name=name,
            description=description,
            image_path=public_url
        )

        db.session.add(new_club)
        try:
            db.session.commit()
            return {
                'message': 'Club created successfully',
                'club': {
                    'id': new_club.id,
                    'name': new_club.name,
                    'description': new_club.description,
                    'image_path': new_club.image_path,
                    'created_at': new_club.created_at.isoformat()
                }
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error creating club', 'error': str(e)}, 500

    def patch(self, club_id):
        club = ClubandSociety.query.get(club_id)
        if not club:
            return {'message': 'Club not found'}, 404

        data = request.form
        image = request.files.get('image')

        club.name = data.get('name', club.name)
        club.description = data.get('description', club.description)

        if image:
            filename = secure_filename(image.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            local_path = os.path.join(UPLOAD_FOLDER, unique_name)
            image.save(local_path)

            try:
                res = cloudinary.uploader.upload(local_path, folder="Clubs")
                public_url = res['secure_url']
                print(f"✅ Updated Cloudinary image: {public_url}")
                club.image_path = public_url
            except Exception as e:
                print(f"⚠️ Cloudinary upload failed: {e}")

        try:
            db.session.commit()
            return {
                'message': 'Club updated successfully',
                'club': {
                    'id': club.id,
                    'name': club.name,
                    'description': club.description,
                    'image_path': club.image_path,
                    'created_at': club.created_at.isoformat()
                }
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error updating club', 'error': str(e)}, 500

    def delete(self, club_id):
        club = ClubandSociety.query.get(club_id)
        if not club:
            return {'message': 'Club not found'}, 404

        if club.image_path:
            try:
                filename_with_ext = club.image_path.split('/')[-1]
                public_id = filename_with_ext.rsplit('.', 1)[0]
                public_id = f"Clubs/{public_id}"
                cloudinary.uploader.destroy(public_id)
                print(f"🗑️ Deleted from Cloudinary: {public_id}")
            except Exception as e:
                print(f"⚠️ Cloudinary delete failed: {e}")

        db.session.delete(club)
        try:
            db.session.commit()
            return {'message': 'Club deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error deleting club', 'error': str(e)}, 500