import sys
import os

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../backend"
        )
    )
)

from app import app


def test_health():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "healthy"
    assert data["service"] == "MediSync API"


def test_get_patients():
    client = app.test_client()

    response = client.get("/patients")

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_doctors():
    client = app.test_client()

    response = client.get("/doctors")

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_appointments():
    client = app.test_client()

    response = client.get("/appointments")

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_missing_patient_name():
    client = app.test_client()

    response = client.post(
        "/patients",
        json={
            "age": 25,
            "email": "missing@example.com"
        }
    )

    assert response.status_code == 400


def test_missing_doctor_name():
    client = app.test_client()

    response = client.post(
        "/doctors",
        json={
            "specialization": "Cardiology"
        }
    )

    assert response.status_code == 400