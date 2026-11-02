from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from config import Config
from extensions import bcrypt, db, migrate
from resources.auth import CheckSession, Login, Logout, Signup
from resources.notes import NoteDetail, NoteList


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.json.sort_keys = False
    # Allow the frontend dev server to send the session cookie.
    CORS(app, supports_credentials=True, origins=["http://localhost:3000", "http://localhost:5173"])

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    api = Api(app)
    api.add_resource(Signup, "/signup")
    api.add_resource(Login, "/login")
    api.add_resource(Logout, "/logout")
    api.add_resource(CheckSession, "/check_session", "/me")
    api.add_resource(NoteList, "/notes")
    api.add_resource(NoteDetail, "/notes/<int:note_id>")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5555, debug=True)
