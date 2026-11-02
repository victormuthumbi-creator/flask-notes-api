from flask import request
from flask_restful import Resource
from marshmallow import ValidationError

from extensions import db
from models import Note
from resources.auth import login_required
from schemas import NoteSchema

MAX_PER_PAGE = 100


def get_owned_note(note_id, user):
    """Fetch a note only if it belongs to `user`. Returns None otherwise,
    so other users' notes look identical to non-existent ones (404)."""
    return Note.query.filter_by(id=note_id, user_id=user.id).first()


def positive_int(value, default):
    try:
        number = int(value)
        return number if number > 0 else default
    except (TypeError, ValueError):
        return default


class NoteList(Resource):
    @login_required
    def get(self, user):
        page = positive_int(request.args.get("page"), 1)
        per_page = min(positive_int(request.args.get("per_page"), 10), MAX_PER_PAGE)

        pagination = (
            Note.query.filter_by(user_id=user.id)
            .order_by(Note.created_at.desc(), Note.id.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )
        return {
            "notes": [n.to_dict() for n in pagination.items],
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }, 200

    @login_required
    def post(self, user):
        try:
            data = NoteSchema().load(request.get_json(silent=True) or {})
        except ValidationError as err:
            return {"errors": err.messages}, 422

        note = Note(title=data["title"], content=data["content"], user_id=user.id)
        db.session.add(note)
        db.session.commit()
        return note.to_dict(), 201


class NoteDetail(Resource):
    @login_required
    def get(self, note_id, user):
        note = get_owned_note(note_id, user)
        if note is None:
            return {"error": "Note not found."}, 404
        return note.to_dict(), 200

    @login_required
    def patch(self, note_id, user):
        note = get_owned_note(note_id, user)
        if note is None:
            return {"error": "Note not found."}, 404

        try:
            data = NoteSchema(partial=True).load(request.get_json(silent=True) or {})
        except ValidationError as err:
            return {"errors": err.messages}, 422

        for field, value in data.items():
            setattr(note, field, value)
        db.session.commit()
        return note.to_dict(), 200

    @login_required
    def delete(self, note_id, user):
        note = get_owned_note(note_id, user)
        if note is None:
            return {"error": "Note not found."}, 404
        db.session.delete(note)
        db.session.commit()
        return {}, 204
