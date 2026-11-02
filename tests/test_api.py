import pytest

from app import create_app
from config import TestConfig
from extensions import db


@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


def signup(client, name="alice"):
    return client.post("/signup", json={"username": name, "password": "secret123"})


def test_signup_login_logout_flow(client):
    assert signup(client).status_code == 201
    assert signup(client).status_code == 409
    assert client.get("/check_session").status_code == 200
    assert client.delete("/logout").status_code == 204
    assert client.get("/check_session").status_code == 401
    assert client.post("/login", json={"username": "alice", "password": "bad"}).status_code == 401
    assert client.post("/login", json={"username": "alice", "password": "secret123"}).status_code == 200


def test_notes_require_auth(client):
    assert client.get("/notes").status_code == 401
    assert client.post("/notes", json={"title": "a", "content": "b"}).status_code == 401


def test_crud_and_pagination(client):
    signup(client)
    for i in range(12):
        assert client.post("/notes", json={"title": f"t{i}", "content": "c"}).status_code == 201
    data = client.get("/notes?page=2&per_page=5").get_json()
    assert len(data["notes"]) == 5 and data["total"] == 12 and data["pages"] == 3
    note_id = data["notes"][0]["id"]
    assert client.patch(f"/notes/{note_id}", json={"title": "new"}).get_json()["title"] == "new"
    assert client.delete(f"/notes/{note_id}").status_code == 204
    assert client.get(f"/notes/{note_id}").status_code == 404
    assert client.post("/notes", json={"title": ""}).status_code == 422


def test_users_cannot_touch_each_others_notes(client):
    signup(client, "alice")
    note_id = client.post("/notes", json={"title": "mine", "content": "x"}).get_json()["id"]
    client.delete("/logout")
    signup(client, "bob")
    assert client.get("/notes").get_json()["total"] == 0
    assert client.get(f"/notes/{note_id}").status_code == 404
    assert client.patch(f"/notes/{note_id}", json={"title": "hax"}).status_code == 404
    assert client.delete(f"/notes/{note_id}").status_code == 404
