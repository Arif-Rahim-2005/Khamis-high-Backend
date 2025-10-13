from models import Department, db
from flask import request
from flask_restful import Resource, reqparse

class DepartmentResource(Resource):
    def get(self, department_id=None):
        if department_id:
            department = Department.query.get(department_id)
            if department:
                return {
                    'id': department.id,
                    'name': department.name,
                    'created_at': department.created_at.isoformat(),
                      'system': {
                        'id': department.system.id,
                        'name': department.system.name
                    },
                    'tracks': [
                        {'id': track.id, 'name': track.name}
                        for track in department.tracks
                    ],
                }, 200
            return {'message': 'Department not found'}, 404
        else:
            departments = Department.query.all()
            return [{
                'id': dept.id,
                'name': dept.name,
                'created_at': dept.created_at.isoformat(),
                 'system': {
                    'id': dept.system.id,
                    'name': dept.system.name
                },
                'tracks': [
                    {'id': track.id, 'name': track.name}
                    for track in dept.tracks
                ],
            } for dept in departments], 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('system_id', required=True, type=int)
        parser.add_argument('name', required=True)
        data = parser.parse_args()
        
        existing = Department.query.filter_by(name=data['name']).first()
        if existing:
            return {'message': 'Department already exists'}, 400

        new_department = Department(
            name=data['name'],
            system_id=data['system_id']
        )
       
        db.session.add(new_department)
        try:
            db.session.commit()
            return {'message': 'Department created successfully', 'id': new_department.id}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': 'An error occurred while creating the department', 'error': str(e)}, 500

    def put(self, department_id):
        data = request.get_json()
        department = Department.query.get(department_id)
        if not department:
            return {'message': 'Department not found'}, 404

        department.name = data.get('name', department.name)
        department.system_id = data.get('system_id', department.system_id)
        try:
            db.session.commit()
            return {'message': 'Department updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'An error occurred while updating the department', 'error': str(e)}, 500
        
    def delete(self, department_id):
        department = Department.query.get(department_id)
        if not department:
            return{"message":"Department not found"}, 404
        db.session.delete(department)
        try:
            db.session.commit()
            return{"message":"Department deleted successfully"}, 200
        except Exception as e :
            return{"message":"An error occurred while deleting the department", "error": str(e)}, 500