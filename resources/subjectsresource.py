from models import db, Subject
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required

class SubjectResource(Resource):
    @jwt_required()
    def get(self, subject_id=None):
        if subject_id:
            subject = Subject.query.get(subject_id)
            if subject:
                return {
                    'id': subject.id,
                    'name': subject.name,
                    'code': subject.code,
                    'description': subject.description,
                    'department_id': subject.department_id,
                    'track_id': subject.track_id
                }, 200
            return {'message': 'Subject not found'}, 404
        else:
            subjects = Subject.query.all()
            return [{
                'id': subj.id,
                'name': subj.name,
                'code': subj.code,
                'description': subj.description,
                'department_id': subj.department_id,
                'track_id': subj.track_id
            } for subj in subjects], 200

    @jwt_required()
    def post(self):
        data = request.get_json()
        new_subject = Subject(
            name=data['name'],
            code=data['code'],
            description=data.get('description'),
            department_id=data['department_id'],
            track_id=data.get('track_id')
        )
        db.session.add(new_subject)
        db.session.commit()
        return {'message': 'Subject created', 'id': new_subject.id}, 201

    @jwt_required()
    def put(self, subject_id):
        data = request.get_json()
        subject = Subject.query.get(subject_id)
        if not subject:
            return {'message': 'Subject not found'}, 404

        subject.name = data.get('name', subject.name)
        subject.code = data.get('code', subject.code)
        subject.description = data.get('description', subject.description)
        subject.department_id = data.get('department_id', subject.department_id)
        subject.track_id = data.get('track_id', subject.track_id)

        db.session.commit()
        return {'message': 'Subject updated'}, 200

    @jwt_required()
    def delete(self, subject_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            return {'message': 'Subject not found'}, 404

        db.session.delete(subject)
        db.session.commit()
        return {'message': 'Subject deleted'}, 200