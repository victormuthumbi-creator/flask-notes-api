# Notes API

A secure Flask REST API for a personal notes app. Users sign up, log in with
cookie-based sessions, and manage their own notes. Nobody can see, edit, or
delete another user's notes.

## Features

- Session-based authentication (signup, login, logout, check session)
- Passwords hashed with Flask-Bcrypt (never stored or returned in plain text)
- `Note` resource owned by a user (`title`, `content`, timestamps, `user_id`)
- Full CRUD with pagination on the index route
- Ownership checks on every note route
- Request validation with Marshmallow
- Database migrations with Flask-Migrate, seed data with Faker

## Project structure

```
app.py            App factory and route registration
config.py         Configuration (dev + test)
extensions.py     db, migrate, bcrypt instances
models.py         User and Note models
schemas.py        Marshmallow validation schemas
resources/        auth.py and notes.py (Flask-RESTful resources)
seed.py           Example data
migrations/       Alembic migrations
tests/            pytest suite
```

## Installation

```bash
pipenv install
pipenv shell
export FLASK_APP=app.py
flask db upgrade     # apply the migrations (creates instance/app.db)
python seed.py       # load example users and notes
```

Seeded users: `alice`, `bob`, `charlie` (password for all: `password123`),
each with 15 notes.

Optional: `export SECRET_KEY="something-long-and-random"` (defaults to a dev key).

## Run

```bash
flask run -p 5555
# or
python app.py
```

The API runs at `http://localhost:5555`. Run the tests with `pytest`.

## Endpoints

Request and response bodies are JSON. Sessions are stored in a cookie, so
clients must send credentials (`credentials: "include"` / Postman cookie jar).

### Auth

| Method | Route | Description | Success | Errors |
|---|---|---|---|---|
| POST | `/signup` | Create an account and log in. Body: `username` (3+ chars), `password` (6+ chars) | 201 | 409 username taken, 422 invalid |
| POST | `/login` | Log in. Body: `username`, `password` | 200 | 401 bad credentials, 422 invalid |
| DELETE | `/logout` | Log out (clears session) | 204 | none |
| GET | `/check_session` (alias `/me`) | Return the logged-in user | 200 | 401 not logged in |

### Notes (login required, own notes only)

| Method | Route | Description | Success | Errors |
|---|---|---|---|---|
| GET | `/notes?page=1&per_page=10` | Paginated list of your notes, newest first. `per_page` max 100. Returns `notes`, `page`, `per_page`, `total`, `pages` | 200 | 401 |
| POST | `/notes` | Create a note. Body: `title`, `content` | 201 | 401, 422 |
| GET | `/notes/<id>` | Get one note | 200 | 401, 404 |
| PATCH | `/notes/<id>` | Update `title` and/or `content` | 200 | 401, 404, 422 |
| DELETE | `/notes/<id>` | Delete a note | 204 | 401, 404 |

Notes belonging to other users return `404`, so their existence is not revealed.
