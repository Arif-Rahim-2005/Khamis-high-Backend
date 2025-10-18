from flask_restful import Resource, reqparse
from models import SubjectSelection, db
import json

class SubjectSelectionResource(Resource):
    # CREATE
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str, required=True, help="Name is required")
        parser.add_argument("subjects", type=list, location="json", required=True, help="Subjects are required")
        parser.add_argument("system_id", type=int, required=True, help="System ID is required")
        parser.add_argument("department_id", type=int, required=True, help="Department ID is required")
        parser.add_argument("track_id", type=int, required=False)

        data = parser.parse_args()

        new_selection = SubjectSelection(
            name=data["name"],
            subjects=json.dumps(data["subjects"]),
            system_id=data["system_id"],
            department_id=data["department_id"],
            track_id=data.get("track_id")
        )

        db.session.add(new_selection)
        try:
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
                "system_id": s.system_id,
                "department_id": s.department_id,
                "track_id": s.track_id
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
