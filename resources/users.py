from flask_restful import Resource, reqparse
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token,jwt_required
from models import db, User
from datetime import timedelta


class LogInResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("email", required=True, help="email is required")
    parser.add_argument("password", required=True, help="password is required")

    def post(self):
        data = self.parser.parse_args()

        user = User.query.filter_by(email=data["email"]).first()

        if user is None:
            return {"message": "invalid email or password"}, 403

        # validate password
        if check_password_hash(user.password_hash, data["password"]):
            # then generate access token
            access_token = create_access_token(
                identity=str(user.id),
                expires_delta=timedelta(hours=24),
            )

            return {
                "message": "Logged in successfully",
                "access_token": access_token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            }, 200
        else:
            return {"message": "invalid email or password"}, 403


class SignUpResource(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument("username", type=str, required=True, help="username is required")
    parser.add_argument("email", type=str, required=True, help="email is required")
    parser.add_argument(
        "password_hash", type=str, required=True, help="password is required"
    )

    def post(self):
        data = self.parser.parse_args()

        email = User.query.filter_by(email=data["email"]).first()

        if email:
            return {"message": "email address is already taken"}, 409

        # encrypt the password
        hash = generate_password_hash(data["password_hash"]).decode("utf-8")

        del data["password_hash"]

        user = User(**data, password_hash=hash)

        db.session.add(user)
        db.session.commit()

        # generate access Token
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role},
            expires_delta=timedelta(hours=24),
        )

        # send email

        return {
            "message": "Account created successfully",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            },
        }, 201

class UserResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("username", type=str)
    parser.add_argument("email", type=str)
    parser.add_argument("role", type=str)

    @jwt_required()
    def get(self, user_id=None):
        if user_id:
            user = User.query.get(user_id)
            if not user:
                return {"message": "User not found"}, 404

            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            }, 200

        # else, get all users
        users = User.query.all()
        return [
            {"id": u.id, "username": u.username, "email": u.email, "role": u.role}
            for u in users
        ], 200

    @jwt_required()
    def patch(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 404

        data = self.parser.parse_args()

        if data["username"]:
            user.username = data["username"]
        if data["email"]:
            user.email = data["email"]
        if data["role"]:
            user.role = data["role"]

        db.session.commit()

        return {
            "message": "User updated successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            },
        }, 200

    @jwt_required()
    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 404

        db.session.delete(user)
        db.session.commit()

        return {"message": "User deleted successfully"}, 200
