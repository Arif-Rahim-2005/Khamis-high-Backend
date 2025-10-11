from flask import request
from flask_restful import Resource
from models import db, User, Subject, Department, Track, System


class SubjectResource(Resource):

    # GET all subjects or one subject by ID
    def get(self, subject_id=None):
        if subject_id:
            subject = Subject.query.get(subject_id)
            if not subject:
                return {'message': 'Subject not found'}, 404

            return {
                'id': subject.id,
                'name': subject.name,
                'department': subject.department.name if subject.department else None,
                'track': subject.track.name if subject.track else None,
                'system': subject.system.name if subject.system else None
            }, 200

        subjects = Subject.query.all()
        return [{
            'id': s.id,
            'name': s.name,
            'department': s.department.name if s.department else None,
            'track': s.track.name if s.track else None,
            'system': s.system.name if s.system else None
        } for s in subjects], 200

    # CREATE a new subject
    def post(self):
        data = request.get_json()

        name = data.get('name')
        system_name = data.get('system')
        department_name = data.get('department')
        track_name = data.get('track')

        if not name or not department_name:
            return {'message': 'Name and department are required'}, 400

        # Check if subject already exists
        existing = Subject.query.filter_by(name=name).first()
        if existing:
            return {'message': 'Subject already exists'}, 400

        # Find related department
        department = Department.query.filter_by(name=department_name).first()
        if not department:
            return {'message': f"Department '{department_name}' not found"}, 404

        # Find related system
        system = System.query.filter_by(name=system_name).first()
        if not system:
            return {'message': f"System '{system_name}' not found"}, 404

        # Find related track (optional)
        track = None
        if track_name:
            track = Track.query.filter_by(name=track_name).first()
            if not track:
                return {'message': f"Track '{track_name}' not found"}, 404

        new_subject = Subject(
            name=name,
            department_id=department.id,
            system_id=system.id,
            track_id=track.id if track else None
        )

        db.session.add(new_subject)
        try:
            db.session.commit()
            return {'message': 'Subject created', 'id': new_subject.id}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error creating subject', 'error': str(e)}, 500

    # UPDATE subject details
    def put(self, subject_id):
        data = request.get_json()
        subject = Subject.query.get(subject_id)

        if not subject:
            return {'message': 'Subject not found'}, 404

        new_name = data.get('name')
        new_department_name = data.get('department')
        new_track_name = data.get('track')
        new_system_name = data.get('system')

        if new_name:
            existing = Subject.query.filter_by(name=new_name).first()
            if existing and existing.id != subject.id:
                return {'message': 'A subject with that name already exists'}, 400
            subject.name = new_name

        if new_department_name:
            department = Department.query.filter_by(name=new_department_name).first()
            if not department:
                return {'message': f"Department '{new_department_name}' not found"}, 404
            subject.department_id = department.id

        if new_track_name:
            track = Track.query.filter_by(name=new_track_name).first()
            if not track:
                return {'message': f"Track '{new_track_name}' not found"}, 404
            subject.track_id = track.id

        if new_system_name:
            system = System.query.filter_by(name=new_system_name).first()
            if not system:
                return {'message': f"System '{new_system_name}' not found"}, 404
            subject.system_id = system.id

        try:
            db.session.commit()
            return {
                'message': 'Subject updated successfully',
                'subject': {
                    'id': subject.id,
                    'name': subject.name,
                    'department': subject.department.name if subject.department else None,
                    'track': subject.track.name if subject.track else None,
                    'system': subject.system.name if subject.system else None
                }
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error updating subject', 'error': str(e)}, 500

    # DELETE a subject
    def delete(self, subject_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            return {'message': 'Subject not found'}, 404

        db.session.delete(subject)
        try:
            db.session.commit()
            return {'message': 'Subject deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error deleting subject', 'error': str(e)}, 500
