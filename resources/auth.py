from functools import wraps

from flask import request, session
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import User
from schemas import LoginSchema, SignupSchema


def login_required(fn):
    """Reject the request with 401 unless a user is logged in; pass the user in."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        user = db.session.get(User, user_id) if user_id else None
        if user is None:
            session.pop("user_id", None)
            return {"error": "Unauthorized. Please log in."}, 401
        return fn(*args, user=user, **kwargs)

    return wrapper


class Signup(Resource):
    def post(self):
        try:
            data = SignupSchema().load(request.get_json(silent=True) or {})
        except ValidationError as err:
            return {"errors": err.messages}, 422

        username = data["username"].strip()
        if User.query.filter_by(username=username).first():
            return {"error": "Username already taken."}, 409

        try:
            user = User(username=username)
            user.password_hash = data["password"]
            db.session.add(user)
            db.session.commit()
        except (IntegrityError, ValueError) as err:
            db.session.rollback()
            return {"error": str(err)}, 422

        session["user_id"] = user.id
        return user.to_dict(), 201


class Login(Resource):
    def post(self):
        try:
            data = LoginSchema().load(request.get_json(silent=True) or {})
        except ValidationError as err:
            return {"errors": err.messages}, 422

        user = User.query.filter_by(username=data["username"].strip()).first()
        if user is None or not user.authenticate(data["password"]):
            return {"error": "Invalid username or password."}, 401

        session["user_id"] = user.id
        return user.to_dict(), 200


class Logout(Resource):
    def delete(self):
        session.pop("user_id", None)
        return {}, 204


class CheckSession(Resource):
    @login_required
    def get(self, user):
        return user.to_dict(), 200
