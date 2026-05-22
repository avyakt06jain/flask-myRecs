import re

import pytest

from myrecs import create_app


@pytest.fixture()
def app(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "DATABASE": str(tmp_path / "test.sqlite3"),
        }
    )
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


def csrf_token(response):
    match = re.search(r'name="_csrf_token" value="([^"]+)"', response.get_data(as_text=True))
    assert match, response.get_data(as_text=True)
    return match.group(1)


def register(client, name="Avi Owner", email="avi@example.com", password="password123"):
    page = client.get("/auth/register")
    return client.post(
        "/auth/register",
        data={
            "_csrf_token": csrf_token(page),
            "name": name,
            "email": email,
            "password": password,
        },
        follow_redirects=True,
    )


def create_record(client, **overrides):
    page = client.get("/records/new")
    data = {
        "_csrf_token": csrf_token(page),
        "buyer_name": "Acme Traders",
        "product_name": "Barcode Scanner",
        "quantity": "2",
        "unit_price": "1499.50",
        "status": "open",
        "notes": "Urgent delivery",
    }
    data.update(overrides)
    return client.post("/records/new", data=data, follow_redirects=True)


def test_user_can_register_and_create_record(client):
    response = register(client)
    assert response.status_code == 200
    assert "Records dashboard" in response.get_data(as_text=True)

    response = create_record(client)
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Acme Traders" in html
    assert "Barcode Scanner" in html
    assert "Rs 2999.00" in html


def test_authentication_required_for_records(client):
    response = client.get("/records/")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_validation_rejects_bad_record(client):
    register(client)
    response = create_record(client, quantity="0", unit_price="-1")
    html = response.get_data(as_text=True)

    assert response.status_code == 400
    assert "Quantity must be a positive whole number." in html
    assert "Unit price must be a valid non-negative amount." in html


def test_record_export_is_scoped_to_signed_in_user(client):
    register(client)
    create_record(client)

    response = client.get("/records/export.csv")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert "Acme Traders" in body
    assert "Barcode Scanner" in body
