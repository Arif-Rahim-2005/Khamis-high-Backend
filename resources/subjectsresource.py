from flask import request
from flask_restful import Resource
from models import db, Subject, Department, Track, System


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
                'track': {
                    'id': subject.track.id if subject.track else None,
                    'name': subject.track.name if subject.track else None
                },
                'department': {
                    'id': subject.department.id if subject.department else None,
                    'name': subject.department.name if subject.department else None
                },

                'system': {
                    'id': subject.system.id,
                    'name': subject.system.name
                } if subject.system else None


            }, 200

        subjects = Subject.query.all()
        return [{
            'id': s.id,
            'name': s.name,
            'track': {
                'id': s.track.id if s.track else None,
                'name': s.track.name if s.track else None
            },
            'department': {
                'id': s.department.id if s.department else None,
                'name': s.department.name if s.department else None
            },
            'system': {
                'id': s.system.id,
                'name': s.system.name
                } if s.system else None
        } for s in subjects], 200

    # CREATE a new subject
    def post(self):
        data = request.get_json()

        name = data.get('name')
        department_id = data.get('department_id')
        system_id = data.get('system_id')
        track_id = data.get('track_id')

        if not name or not department_id:
            return {'message': 'Name and department_id are required'}, 400

        # existing = Subject.query.filter_by(name=name).first()
        # if existing:
        #     return {'message': 'Subject already exists'}, 400
        existing = Subject.query.filter_by(name=name, system_id=system_id).first()
        if existing:
            return {'message': f"Subject '{name}' already exists in this system"}, 400


        department = Department.query.get(department_id)
        if not department:
            return {'message': f"Department ID {department_id} not found"}, 404

        system = System.query.get(system_id) if system_id else None
        track = Track.query.get(track_id) if track_id else None

        new_subject = Subject(
            name=name,
            department_id=department.id,
            system_id=system.id if system else None,
            track_id=track.id if track else None
        )

        db.session.add(new_subject)
        try:
            db.session.commit()
            return {
                'message': 'Subject created successfully',
                'subject': {
                    'id': new_subject.id,
                    'name': new_subject.name,
                    'department': {'id': department.id, 'name': department.name},
                    'system': {'id': system.id, 'name': system.name} if system else None,
                    'track': {'id': track.id, 'name': track.name} if track else None
                }
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error creating subject', 'error': str(e)}, 500

    # UPDATE subject details
    def patch(self, subject_id):
        data = request.get_json()
        subject = Subject.query.get(subject_id)

        if not subject:
            return {'message': 'Subject not found'}, 404

        # Get new values if provided
        new_name = data.get('name')
        new_department_name = data.get('department')
        new_track_name = data.get('track')
        new_system_name = data.get('system')

        # Update name
        if new_name and new_name != subject.name:
            print("Incoming PATCH data:", data)
            print("Current subject name:", subject.name)
            existing = Subject.query.filter_by(name=new_name).first()
            if existing and existing.id != subject.id:
                return {'message': 'A subject with that name already exists'}, 400
            subject.name = new_name

        # Update department
        if new_department_name:
            department = Department.query.filter_by(name=new_department_name).first()
            if not department:
                return {'message': f"Department '{new_department_name}' not found"}, 404
            subject.department_id = department.id

        # Update track
        if new_track_name:
            track = Track.query.filter_by(name=new_track_name).first()
            if not track:
                return {'message': f"Track '{new_track_name}' not found"}, 404
            subject.track_id = track.id

        # Update system
        if new_system_name:
            system = System.query.filter_by(name=new_system_name).first()
            if not system:
                return {'message': f"System '{new_system_name}' not found"}, 404
            subject.system_id = system.id

        # Commit changes
        try:
            db.session.commit()

            # Re-fetch the updated subject with relationships
            updated_subject = Subject.query.get(subject.id)

            return {
                'message': 'Subject updated successfully',
                'subject': {
                    'id': updated_subject.id,
                    'name': updated_subject.name,
                    'track': {
                        'id': updated_subject.track.id if updated_subject.track else None,
                        'name': updated_subject.track.name if updated_subject.track else None
                    },
                    'department': {
                        'id': updated_subject.department.id if updated_subject.department else None,
                        'name': updated_subject.department.name if updated_subject.department else None
                    },
                    'system': {
                        'id': updated_subject.system.id if updated_subject.system else None,
                        'name': updated_subject.system.name if updated_subject.system else None
                    }
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
