from models import System, db
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required

class SystemResource(Resource):
    @jwt_required()
    def get(self, system_id=None):
        if system_id:
            system = System.query.get(system_id)
            if system:
                return {
                    'id': system.id,
                    'name': system.name,
                    'description': system.description,
                    'created_at': system.created_at.isoformat()
                }, 200
            return {'message': 'System not found'}, 404
        else:
            systems = System.query.all()
            return [{
                'id': sys.id,
                'name': sys.name,
                'description': sys.description,
                'created_at': sys.created_at.isoformat()
            } for sys in systems], 200

    @jwt_required()
    def post(self):
        data = request.get_json()
        new_system = System(
            name=data['name'],
            description=data.get('description')
        )
        existing = System.query.filter_by(name=data['name']).first()
        if existing:
            return {'message': 'System already exists'}, 400

        db.session.add(new_system)
        try:
            db.session.commit()
            return {'message': 'System created', 'id': new_system.id}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': 'An error occurred while creating the system', 'error': str(e)}, 500
        
    @jwt_required()
    def put(self, system_id):
        data = request.get_json()
        system = System.query.get(system_id)
        if not system:
            return {'message': 'System not found'}, 404

        system.name = data.get('name', system.name)
        system.description = data.get('description', system.description)
        try:
            db.session.commit()
            return {'message': 'System updated'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'An error occurred while updating the system', 'error': str(e)}, 500
    
    @jwt_required()
    def delete(self, system_name):
        system = System.query.filter_by(name=system_name).first()
        if not system:
            return{"message":"System not found"}, 404
        db.session.delete(system)
        try:

            db.session.commit()
            return{"message":"System deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return{"message":"An error occurred while deleting the system", "error": str(e)}, 500