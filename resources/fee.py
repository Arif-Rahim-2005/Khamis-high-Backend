# # routes.py
# from flask import Blueprint, request, send_from_directory, jsonify
# from werkzeug.utils import secure_filename
# import os
# from models import db, FeeStructure

# fee_bp = Blueprint("fee", __name__)
# UPLOAD_FOLDER = "uploads/fee_structures"
# ALLOWED_EXTENSIONS = {"pdf"}

# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# def allowed_file(filename):
#     return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# # Upload / replace PDF (Admin only)
# @fee_bp.route("/fee-structure", methods=["POST"])
# def upload_fee_structure():
#     # In practice, check admin authentication here!
#     if "file" not in request.files:
#         return jsonify({"message": "No file provided"}), 400

#     file = request.files["file"]
#     if not allowed_file(file.filename):
#         return jsonify({"message": "Invalid file type"}), 400

#     filename = secure_filename("fee_structure.pdf")  # always same name
#     file_path = os.path.join(UPLOAD_FOLDER, filename)
#     file.save(file_path)

#     # Only one row allowed: either update existing or create
#     fee = FeeStructure.query.first()
#     if fee:
#         fee.file_path = file_path
#     else:
#         fee = FeeStructure(file_path=file_path)
#         db.session.add(fee)
#     db.session.commit()

#     return jsonify({"message": "Fee structure uploaded successfully"}), 200

# # Fetch the current PDF
# @fee_bp.route("/fee-structure", methods=["GET"])
# def get_fee_structure():
#     fee = FeeStructure.query.first()
#     if not fee:
#         return jsonify({"message": "No fee structure found"}), 404

#     # Return file URL (frontend can use it in <iframe>)
#     return jsonify({"file_path": f"/fee-structure-file/{os.path.basename(fee.file_path)}"})


# # Serve the file
# @fee_bp.route("/fee-structure-file/<filename>")
# def serve_fee_structure(filename):
#     return send_from_directory(UPLOAD_FOLDER, filename)

# resources/fee_structure.py
from flask_restful import Resource
from flask import request, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import os
from models import db, FeeStructure

UPLOAD_FOLDER = "uploads/fee_structures"
ALLOWED_EXTENSIONS = {"pdf"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


class FeeStructureResource(Resource):
    # GET current fee structure
    def get(self):
        fee = FeeStructure.query.first()
        if not fee:
            return {"message": "No fee structure found"}, 404

        return {
            "file_path": f"/fee-structure-file/{os.path.basename(fee.file_path)}"
        }, 200

    # POST upload / replace PDF (Admin only)
    def post(self):
        # TODO: add proper admin authentication here
        if "file" not in request.files:
            return {"message": "No file provided"}, 400

        file = request.files["file"]
        if not allowed_file(file.filename):
            return {"message": "Invalid file type"}, 400

        filename = secure_filename("fee_structure.pdf")  # always same name
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Only one row allowed: either update existing or create
        fee = FeeStructure.query.first()
        if fee:
            fee.file_path = file_path
        else:
            fee = FeeStructure(file_path=file_path)
            db.session.add(fee)
        db.session.commit()

        return {"message": "Fee structure uploaded successfully"}, 200


class ServeFeeStructureFile(Resource):
    def get(self, filename):
        return send_from_directory(UPLOAD_FOLDER, filename)
