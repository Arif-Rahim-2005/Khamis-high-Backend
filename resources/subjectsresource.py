from models import db, Subject
from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity

class SubjectResource(Resource):

    def get(self, subject_id=None):
        if subject_id:
            subject = Subject.query.get(subject_id)
            if subject:
                return {
                    'name': subject.name,
                    'code': subject.code,
                    'description': subject.description,
                }, 200
            return {'message': 'Subject not found'}, 404
        else:
            subjects = Subject.query.all()
            return [{
                'name': subj.name,
                'code': subj.code,
                'description': subj.description
            } for subj in subjects], 200

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()

        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        parser.add_argument('code', required=True)
        args = parser.parse_args()

        existing = Subject.query.filter_by(name=args['name']).first()
        if existing:
            return {'message': 'Subject already exists'}, 400
        new_subject = Subject(
            name=args.get('name'),
            code=args.get('code'),
        )
        db.session.add(new_subject)
        try:
            db.session.commit()
            return {'message': 'Subject created', 'id': new_subject.id}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error creating subject', 'error': str(e)}, 500

    @jwt_required()
    def put(self, subject_id):
        user_id = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        parser.add_argument('code', required=True)
        parser.add_argument('description', required=True)
        args = parser.parse_args()

        subject = Subject.query.get(subject_id)
        if not subject:
            return {'message': 'Subject not found'}, 404

        subject.name = args.get('name', subject.name)
        subject.code = args.get('code', subject.code)
        subject.description = args.get('description', subject.description)
        subject.department_id = args.get('department_id', subject.department_id)
        subject.track_id = args.get('track_id', subject.track_id)

        try:
            db.session.commit()
            return {'message': 'Subject updated'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error updating subject', 'error': str(e)}, 500

    @jwt_required()
    def delete(self, subject_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            return {'message': 'Subject not found'}, 404

        db.session.delete(subject)
        try:
            db.session.commit()
            return {'message': 'Subject deleted'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error deleting subject', 'error': str(e)}, 500