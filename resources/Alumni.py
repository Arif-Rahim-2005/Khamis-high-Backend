from flask import request, jsonify, send_from_directory
from flask_restful import Resource
from werkzeug.utils import secure_filename
from models import db, Alumni
import os

# Folder where alumni images will be stored
UPLOAD_FOLDER = os.path.join("uploads", "Alumni")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class AlumniResource(Resource):
    def get(self, id=None):
        """Get all alumni or a specific one by ID"""
        if id:
            alumni = Alumni.query.get_or_404(id)
            return jsonify({
                "id": alumni.id,
                "name": alumni.name,
                "current_title": alumni.current_title,
                "year_of_completion": alumni.year_of_completion,
                "comment": alumni.comment,
                "image_path": f"/uploads/Alumni/{alumni.image_path}" if alumni.image_path else None,
            })

        alumni_list = Alumni.query.all()
        return jsonify({
            "alumni": [
                {
                    "id": a.id,
                    "name": a.name,
                    "current_title": a.current_title,
                    "year_of_completion": a.year_of_completion,
                    "comment": a.comment,
                    "image_path": f"/uploads/Alumni/{a.image_path}" if a.image_path else None,
                } for a in alumni_list
            ]
        })

    def post(self):
        """Add new alumni"""
        name = request.form.get("name")
        current_title = request.form.get("current_title")
        year_of_completion = request.form.get("year_of_completion")
        comment = request.form.get("comment")
        image = request.files.get("image")

        if not name or not comment:
            return {"message": "Name and comment are required."}, 400

        image_filename = None
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, filename))
            image_filename = filename

        new_alumni = Alumni(
            name=name,
            current_title=current_title,
            year_of_completion=year_of_completion,
            comment=comment,
            image_path=image_filename,
        )
        db.session.add(new_alumni)
        db.session.commit()

        return {"message": "Alumni added successfully!"}, 201

    def put(self, id):
        """Edit existing alumni"""
        alumni = Alumni.query.get_or_404(id)

        alumni.name = request.form.get("name", alumni.name)
        alumni.current_title = request.form.get("current_title", alumni.current_title)
        alumni.year_of_completion = request.form.get("year_of_completion", alumni.year_of_completion)
        alumni.comment = request.form.get("comment", alumni.comment)

        image = request.files.get("image")
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, filename))
            alumni.image_path = filename

        db.session.commit()
        return {"message": "Alumni updated successfully!"}, 200

    def delete(self, id):
        """Delete alumni"""
        alumni = Alumni.query.get_or_404(id)
        if alumni.image_path:
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, alumni.image_path))
            except FileNotFoundError:
                pass

        db.session.delete(alumni)
        db.session.commit()
        return {"message": "Alumni deleted successfully!"}, 200


# ✅ Serve uploaded images directly
def register_upload_route(app):
    @app.route("/uploads/Alumni/<filename>")
    def uploaded_file(filename):
        return send_from_directory(UPLOAD_FOLDER, filename)
