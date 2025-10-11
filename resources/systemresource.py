from models import System, db
from flask import request
from flask_restful import Resource, reqparse

class SystemResource(Resource):
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

    def post(self):
        reparse = reqparse.RequestParser()
        reparse.add_argument('name', required=True)
        data = reparse.parse_args()
        existing = System.query.filter_by(name=data['name']).first()
        if existing:
            return {'message': 'System already exists'}, 400

        new_system = System(
            name=data['name'],
        )
       
        db.session.add(new_system)
        try:
            db.session.commit()
            return {'message': 'System created', 'id': new_system.id}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': 'An error occurred while creating the system', 'error': str(e)}, 500

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
    
    def delete(self, system_id):
        system = System.query.filter_by(id=system_id).first()
        if not system:
            return{"message":"System not found"}, 404
        db.session.delete(system)
        try:

            db.session.commit()
            return{"message":"System deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return{"message":"An error occurred while deleting the system", "error": str(e)}, 500