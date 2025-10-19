from flask_restful import Resource, reqparse , request
from models import SubjectSelection, db
import json

class SubjectSelectionResource(Resource):
    # CREATE
    def post(self):
        try:
            data = request.get_json()  # <-- directly get the JSON payload
            # Validate required fields
            required_fields = ["name", "subjects", "system_id", "department_id"]
            for field in required_fields:
                if field not in data or not data[field]:
                    return {"message": f"{field} is required"}, 400

            new_selection = SubjectSelection(
                name=data["name"],
                subjects=json.dumps(data["subjects"]),  # store as JSON string
                system_id=int(data["system_id"]),
                department_id=int(data["department_id"]),
                track_id=int(data.get("track_id")) if data.get("track_id") else None
            )

            db.session.add(new_selection)
            db.session.commit()

            return {
                "message": "Selection added successfully",
                "selection": {
                    "id": new_selection.id,
                    "name": new_selection.name,
                    "subjects": json.loads(new_selection.subjects),
                    "system_id": new_selection.system_id,
                    "department_id": new_selection.department_id,
                    "track_id": new_selection.track_id
                }
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"message": "Error creating subject selection", "error": str(e)}, 500
    # READ ALL
    def get(self):
        selections = SubjectSelection.query.all()
        result = [
                {
                    "id": s.id,
                    "name": s.name,
                    "subjects": json.loads(s.subjects),
                    "system": {
                        "id": s.system.id if s.system else None,
                        "name": s.system.name if s.system else None
                    },
                    "department": {
                        "id": s.department.id if s.department else None,
                        "name": s.department.name if s.department else None
                    },
                    "track": {
                        "id": s.track.id if s.track else None,
                        "name": s.track.name if s.track else None
                    }
                } for s in selections
            ]
        return result, 200


class SubjectSelectionByIdResource(Resource):
    # READ SINGLE
    def get(self, selection_id):
        selection = SubjectSelection.query.get(selection_id)
        if not selection:
            return {"message": "Selection not found"}, 404

        return {
            "id": selection.id,
            "name": selection.name,
            "subjects": json.loads(selection.subjects),
            "system_id": selection.system_id,
            "department_id": selection.department_id,
            "track_id": selection.track_id
        }, 200

    # UPDATE
    def patch(self, selection_id):
        selection = SubjectSelection.query.get(selection_id)
        if not selection:
            return {"message": "Selection not found"}, 404

        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str)
        parser.add_argument("subjects", type=list, location="json")
        parser.add_argument("system_id", type=int)
        parser.add_argument("department_id", type=int)
        parser.add_argument("track_id", type=int)
        data = parser.parse_args()

        if data["name"]:
            selection.name = data["name"]
        if data["subjects"]:
            selection.subjects = json.dumps(data["subjects"])
        if data["system_id"]:
            selection.system_id = data["system_id"]
        if data["department_id"]:
            selection.department_id = data["department_id"]
        if data["track_id"] is not None:
            selection.track_id = data["track_id"]

        db.session.commit()

        return {
            "message": "Selection updated successfully",
            "selection": {
                "id": selection.id,
                "name": selection.name,
                "subjects": json.loads(selection.subjects),
                "system_id": selection.system_id,
                "department_id": selection.department_id,
                "track_id": selection.track_id
            }
        }, 200

    # DELETE
    def delete(self, selection_id):
        selection = SubjectSelection.query.get(selection_id)
        if not selection:
            return {"message": "Selection not found"}, 404

        db.session.delete(selection)
        db.session.commit()
        return {"message": "Selection deleted successfully"}, 200
