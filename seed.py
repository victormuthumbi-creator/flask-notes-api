"""Populate the database with example users and notes.

Run with: python seed.py   (re-running wipes and recreates the data)
"""
from faker import Faker

from app import app
from extensions import db
from models import Note, User

fake = Faker()

USERS = [("alice", "password123"), ("bob", "password123"), ("charlie", "password123")]
NOTES_PER_USER = 15  # enough to demonstrate pagination


def seed():
    Note.query.delete()
    User.query.delete()

    for username, password in USERS:
        user = User(username=username)
        user.password_hash = password
        db.session.add(user)
        db.session.flush()

        for _ in range(NOTES_PER_USER):
            db.session.add(
                Note(
                    title=fake.sentence(nb_words=4).rstrip("."),
                    content=fake.paragraph(nb_sentences=3),
                    user_id=user.id,
                )
            )
    db.session.commit()
    print(f"Seeded {len(USERS)} users and {len(USERS) * NOTES_PER_USER} notes.")


if __name__ == "__main__":
    with app.app_context():
        seed()
