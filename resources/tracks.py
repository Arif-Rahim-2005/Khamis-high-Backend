from models import Track, db
from flask_restful import Resource, reqparse
from flask import request

class TrackResource(Resource):
    def get(self, track_id=None):
        if track_id:
            track= Track.query.get(track_id)
            if not track:
                return {"message": "Track not found"}, 404

            return{
                'id':track.id,
                'name':track.name,
                'department':track.department.name
            }, 200
        else:
            tracks= Track.query.all()
            return[{
                'id':track.id,
                'name':track.name,
                'department':track.department.name
            
                } for track in tracks ], 200
        
    def post(self):
        parser= reqparse.RequestParser()
        parser.add_argument('department_id', required=True, type=int)
        parser.add_argument('name', required=True)
        data=parser.parse_args()

        existing_track= Track.query.filter_by(name=data['name']).first()

        if existing_track:
            return{"message":"Track already exists"}, 400
        
        new_track= Track(
            name=data['name'],
            department_id=data['department_id']
        )

        db.session.add(new_track)
        try:
            db.session.commit()
            return{"message":"Track added successfully"}, 201
        except Exception as e:
            return{"message":"An error occurred while adding the track", 'error':str(e) }, 500
            

    def patch(self, track_id):
        data=request.get_json()
        track= Track.query.filter_by(id=track_id).first()
        if not track:
            return{"message":"Track does not exist"}, 404
        
        track.name=data.get('name', track.name)
        track.department_id=data.get('department_id', track.department_id)
        try:
            db.session.commit()
            return{"message":"Track updated successfully"}, 200
        except Exception as e:
            return{"message":"An error occurred when updating the track", "error":str(e)}, 500

    def delete(self, track_id):
        track=Track.query.filter_by(id=track_id).first()
        if not track:
            return{"message":"Track not found"}, 404
        db.session.delete(track)
        try:
            db.session.commit()
            return{"message":"Track deleted successfully"}, 200
        except Exception as e:
            return {"message":"An error occurred when deleting the track", "error":str(e)}, 500