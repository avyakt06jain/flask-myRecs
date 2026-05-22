# MyRecs

MyRecs is a Flask-based record management web application for tracking buyers, products, quantities, prices, payment status, and notes in a clean account-based workspace. The application provides persistent storage, authentication, searchable records, dashboard metrics, CSV export, and server-side validation.

Live app: https://flask-my-recs-gpow.vercel.app/

## Features

- User registration, login, and logout
- Password hashing with Werkzeug
- User-scoped records so each account only sees its own data
- Create, edit, delete, search, and filter records
- Track record status as open, paid, or cancelled
- Dashboard metrics for total records, total value, open value, and paid value
- CSV export for filtered record data
- SQLite persistence with schema constraints, indexes, and timestamps
- CSRF protection for form submissions
- Security response headers
- Responsive HTML/CSS interface
- Pytest test coverage for core workflows

## Tech Stack

- Python
- Flask
- SQLite
- Jinja2 templates
- HTML/CSS
- Werkzeug security utilities
- Pytest
- Vercel deployment configuration

## Architecture

The application uses a Flask app factory pattern with separate modules for authentication, records, database access, and security concerns. Routes are grouped using Flask blueprints, while SQLite is used as the persistence layer.

```text
Browser
  |
  v
Flask app factory
  |
  +-- Auth blueprint
  |     +-- register
  |     +-- login
  |     +-- logout
  |
  +-- Records blueprint
  |     +-- dashboard
  |     +-- create record
  |     +-- edit record
  |     +-- delete record
  |     +-- export CSV
  |
  +-- Security helpers
  |     +-- current user loading
  |     +-- login_required
  |     +-- CSRF validation
  |     +-- response headers
  |
  v
SQLite database
```

## Project Structure

```text
flask-myRecs/
├── main.py
├── requirements.txt
├── vercel.json
├── README.md
├── myrecs
│   ├── __init__.py
│   ├── auth.py
│   ├── database.py
│   ├── records.py
│   └── security.py
├── static
│   └── css
│       └── app.css
├── templates
│   ├── base.html
│   ├── auth
│   │   ├── login.html
│   │   └── register.html
│   └── records
│       ├── dashboard.html
│       └── form.html
└── tests
    └── test_app.py
```

## Key Files

- `main.py`: WSGI entry point used by Flask and deployment platforms.
- `myrecs/__init__.py`: Creates and configures the Flask app.
- `myrecs/auth.py`: Handles registration, login, and logout.
- `myrecs/database.py`: Manages SQLite connections, schema creation, and demo seeding.
- `myrecs/records.py`: Contains record dashboard, CRUD, filtering, metrics, and CSV export logic.
- `myrecs/security.py`: Provides login checks, CSRF validation, current user loading, and security headers.
- `templates/`: Jinja2 templates for the UI.
- `static/css/app.css`: Application styling.
- `tests/test_app.py`: Automated tests for authentication, protected routes, validation, and exports.

## Run Locally

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Set a secret key:

```bash
export SECRET_KEY="change-this-in-production"
```

Initialize the database:

```bash
flask --app main init-db
```

Optionally seed demo data:

```bash
flask --app main init-db --seed-demo
```

Start the development server:

```bash
flask --app main run
```

Open the app at:

```text
http://127.0.0.1:5000
```

## Demo Account

If the database is initialized with `--seed-demo`, use:

```text
Email: demo@myrecs.local
Password: password123
```

## Running Tests

```bash
pytest
```

Or with the project virtual environment:

```bash
.venv/bin/python -m pytest -q
```

## Environment Variables

| Variable | Description | Required |
| --- | --- | --- |
| `SECRET_KEY` | Flask session signing key | Recommended for all non-local runs |

## Database

MyRecs uses SQLite by default. The database file is created inside the `instance/` directory. The schema includes:

- `users`: account data with hashed passwords
- `records`: user-owned buyer/product records with quantity, price, status, notes, and timestamps

The application enables SQLite foreign keys and uses indexes for common user-scoped record queries.

## Deployment

The repository includes `vercel.json` for Vercel deployment using `main.py` as the Python entry point.

Live deployment:

```text
https://flask-my-recs-gpow.vercel.app/
```
