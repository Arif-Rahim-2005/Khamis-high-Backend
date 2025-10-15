from flask_restful import Resource, reqparse
from models import SubjectSelection, db
import json

class SubjectSelectionResource(Resource):
    # CREATE
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str, required=True, help="Name is required")
        parser.add_argument("subjects", type=list, location="json", required=True, help="Subjects are required")
        data = parser.parse_args()

        new_selection = SubjectSelection(
            name=data["name"],
            subjects=json.dumps(data["subjects"])
        )

        db.session.add(new_selection)
        try:
            db.session.commit()

            return {
                "message": "Selection added successfully",
                "selection": {
                    "id": new_selection.id,
                    "name": new_selection.name,
                    "subjects": json.loads(new_selection.subjects)
                }
            }, 201
        except Exception as e:
            return {"Message":"error while creating the subject selection",'error':str(e)}

    # READ ALL
    def get(self):
        selections = SubjectSelection.query.all()
        result = [
            {
                "id": s.id,
                "name": s.name,
                "subjects": json.loads(s.subjects)
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
            "subjects": json.loads(selection.subjects)
        }, 200

    # UPDATE
    def patch(self, selection_id):
        selection = SubjectSelection.query.get(selection_id)
        if not selection:
            return {"message": "Selection not found"}, 404

        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str)
        parser.add_argument("subjects", type=list, location="json")
        data = parser.parse_args()

        if data["name"]:
            selection.name = data["name"]
        if data["subjects"]:
            selection.subjects = json.dumps(data["subjects"])

        db.session.commit()

        return {
            "message": "Selection updated successfully",
            "selection": {
                "id": selection.id,
                "name": selection.name,
                "subjects": json.loads(selection.subjects)
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
