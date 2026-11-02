"""Marshmallow schemas used to validate incoming request bodies."""
from marshmallow import Schema, fields, validate


class SignupSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))


class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class NoteSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    content = fields.Str(required=True, validate=validate.Length(min=1))
