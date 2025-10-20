import os
from flask import request, current_app as app, url_for
from flask_restful import Resource, reqparse
from werkzeug.utils import secure_filename
from models import ClubandSociety, db

# Folder where club images will be stored
UPLOAD_FOLDER = os.path.join("uploads", "Clubs")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
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
                'image_path': f"/uploads/Clubs/{club.image_path}" if club.image_path else None,
                'created_at': club.created_at.isoformat()
            }, 200

        # Get all clubs
        clubs = ClubandSociety.query.all()
        return [{
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'image_path': f"/uploads/Clubs/{c.image_path}" if c.image_path else None,
            'created_at': c.created_at.isoformat()
        } for c in clubs], 200


    def post(self):
        name = request.form.get('name')
        description = request.form.get('description', '')
        image = request.files.get('image')

        # check for existing club
        existing = ClubandSociety.query.filter_by(name=name).first()
        if existing:
            return {'message': 'Club already exists'}, 400

        # handle image upload
        image_filename = None
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, filename))
            image_filename = filename

        new_club = ClubandSociety(
            name=name,
            description=description,
            image_path=image_filename
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
                    'image_path':f"/uploads/Clubs/{new_club.image_path}" if new_club.image_path else None,
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

        # handle image update
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, filename))
            club.image_path = filename

        try:
            db.session.commit()
            return {
                'message': 'Club updated successfully',
                'club': {
                    'id': club.id,
                    'name': club.name,
                    'description': club.description,
                    'image_path': f"/uploads/Clubs/{club.image_path}" if club.image_path else None,
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
                os.remove(os.path.join(UPLOAD_FOLDER, club.image_path))
            except FileNotFoundError:
                pass


        db.session.delete(club)
        try:
            db.session.commit()
            return {'message': 'Club deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error deleting club', 'error': str(e)}, 500
