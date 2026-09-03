from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://medisync_user:medisync_password@localhost:5432/medisync"
)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================
# DATABASE MODELS
# =========================

class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)


class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.id"),
        nullable=False
    )
    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.id"),
        nullable=False
    )
    appointment_date = db.Column(db.String(20), nullable=False)
    appointment_time = db.Column(db.String(10), nullable=False)
    status = db.Column(
        db.String(30),
        default="scheduled"
    )


# =========================
# WEB PAGES
# =========================

@app.route("/")
def dashboard():

    patient_count = Patient.query.count()
    doctor_count = Doctor.query.count()
    appointment_count = Appointment.query.count()

    appointments = Appointment.query.order_by(
        Appointment.id.desc()
    ).limit(10).all()

    appointment_data = []

    for appointment in appointments:

        patient = db.session.get(
            Patient,
            appointment.patient_id
        )

        doctor = db.session.get(
            Doctor,
            appointment.doctor_id
        )

        appointment_data.append({
            "id": appointment.id,
            "patient": patient.name if patient else "Unknown",
            "doctor": doctor.name if doctor else "Unknown",
            "date": appointment.appointment_date,
            "time": appointment.appointment_time,
            "status": appointment.status
        })

    return render_template(
        "index.html",
        patient_count=patient_count,
        doctor_count=doctor_count,
        appointment_count=appointment_count,
        appointments=appointment_data
    )


@app.route("/patients-page")
def patients_page():

    patients = Patient.query.order_by(
        Patient.id.desc()
    ).all()

    return render_template(
        "patients.html",
        patients=patients
    )


@app.route("/doctors-page")
def doctors_page():

    doctors = Doctor.query.order_by(
        Doctor.id.desc()
    ).all()

    return render_template(
        "doctors.html",
        doctors=doctors
    )


@app.route("/appointments-page")
def appointments_page():

    appointments = Appointment.query.order_by(
        Appointment.id.desc()
    ).all()

    appointment_data = []

    for appointment in appointments:

        patient = db.session.get(
            Patient,
            appointment.patient_id
        )

        doctor = db.session.get(
            Doctor,
            appointment.doctor_id
        )

        appointment_data.append({
            "id": appointment.id,
            "patient": patient.name if patient else "Unknown",
            "doctor": doctor.name if doctor else "Unknown",
            "date": appointment.appointment_date,
            "time": appointment.appointment_time,
            "status": appointment.status
        })

    patients = Patient.query.all()
    doctors = Doctor.query.all()

    return render_template(
        "appointments.html",
        appointments=appointment_data,
        patients=patients,
        doctors=doctors
    )


# =========================
# WEB FORM ACTIONS
# =========================

@app.route("/add-patient", methods=["POST"])
def add_patient():

    name = request.form.get("name")
    age = request.form.get("age")
    email = request.form.get("email")

    if not name or not age or not email:
        return redirect(url_for("patients_page"))

    existing = Patient.query.filter_by(
        email=email
    ).first()

    if existing:
        return redirect(url_for("patients_page"))

    patient = Patient(
        name=name,
        age=int(age),
        email=email
    )

    db.session.add(patient)
    db.session.commit()

    return redirect(url_for("patients_page"))


@app.route("/add-doctor", methods=["POST"])
def add_doctor():

    name = request.form.get("name")
    specialization = request.form.get("specialization")

    if not name or not specialization:
        return redirect(url_for("doctors_page"))

    doctor = Doctor(
        name=name,
        specialization=specialization
    )

    db.session.add(doctor)
    db.session.commit()

    return redirect(url_for("doctors_page"))


@app.route("/add-appointment", methods=["POST"])
def add_appointment():

    patient_id = request.form.get("patient_id")
    doctor_id = request.form.get("doctor_id")
    date = request.form.get("date")
    time = request.form.get("time")

    if not patient_id or not doctor_id or not date or not time:
        return redirect(url_for("appointments_page"))

    patient = db.session.get(
        Patient,
        int(patient_id)
    )

    doctor = db.session.get(
        Doctor,
        int(doctor_id)
    )

    if not patient or not doctor:
        return redirect(url_for("appointments_page"))

    appointment = Appointment(
        patient_id=int(patient_id),
        doctor_id=int(doctor_id),
        appointment_date=date,
        appointment_time=time,
        status="scheduled"
    )

    db.session.add(appointment)
    db.session.commit()

    return redirect(url_for("appointments_page"))


@app.route("/cancel-appointment/<int:appointment_id>", methods=["POST"])
def cancel_appointment_page(appointment_id):

    appointment = db.session.get(
        Appointment,
        appointment_id
    )

    if appointment:
        appointment.status = "cancelled"
        db.session.commit()

    return redirect(url_for("appointments_page"))


# =========================
# REST API
# =========================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "healthy",
        "service": "MediSync API",
        "version": "1.0.0"
    })


@app.route("/patients", methods=["GET"])
def get_patients():

    patients = Patient.query.all()

    return jsonify([
        {
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "email": patient.email
        }
        for patient in patients
    ])


@app.route("/patients", methods=["POST"])
def create_patient():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    required_fields = [
        "name",
        "age",
        "email"
    ]

    for field in required_fields:

        if field not in data:

            return jsonify({
                "error": f"{field} is required"
            }), 400

    existing_patient = Patient.query.filter_by(
        email=data["email"]
    ).first()

    if existing_patient:

        return jsonify({
            "error": "Patient already exists"
        }), 409

    patient = Patient(
        name=data["name"],
        age=data["age"],
        email=data["email"]
    )

    db.session.add(patient)
    db.session.commit()

    return jsonify({
        "message": "Patient created",
        "patient": {
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "email": patient.email
        }
    }), 201


@app.route("/doctors", methods=["GET"])
def get_doctors():

    doctors = Doctor.query.all()

    return jsonify([
        {
            "id": doctor.id,
            "name": doctor.name,
            "specialization": doctor.specialization
        }
        for doctor in doctors
    ])


@app.route("/doctors", methods=["POST"])
def create_doctor():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    if "name" not in data:

        return jsonify({
            "error": "name is required"
        }), 400

    if "specialization" not in data:

        return jsonify({
            "error": "specialization is required"
        }), 400

    doctor = Doctor(
        name=data["name"],
        specialization=data["specialization"]
    )

    db.session.add(doctor)
    db.session.commit()

    return jsonify({
        "message": "Doctor created",
        "doctor": {
            "id": doctor.id,
            "name": doctor.name,
            "specialization": doctor.specialization
        }
    }), 201


@app.route("/appointments", methods=["GET"])
def get_appointments():

    appointments = Appointment.query.all()

    return jsonify([
        {
            "id": appointment.id,
            "patient_id": appointment.patient_id,
            "doctor_id": appointment.doctor_id,
            "date": appointment.appointment_date,
            "time": appointment.appointment_time,
            "status": appointment.status
        }
        for appointment in appointments
    ])


@app.route("/appointments", methods=["POST"])
def create_appointment():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    required_fields = [
        "patient_id",
        "doctor_id",
        "date",
        "time"
    ]

    for field in required_fields:

        if field not in data:

            return jsonify({
                "error": f"{field} is required"
            }), 400

    patient = db.session.get(
        Patient,
        data["patient_id"]
    )

    doctor = db.session.get(
        Doctor,
        data["doctor_id"]
    )

    if not patient:

        return jsonify({
            "error": "Patient not found"
        }), 404

    if not doctor:

        return jsonify({
            "error": "Doctor not found"
        }), 404

    appointment = Appointment(
        patient_id=data["patient_id"],
        doctor_id=data["doctor_id"],
        appointment_date=data["date"],
        appointment_time=data["time"],
        status="scheduled"
    )

    db.session.add(appointment)
    db.session.commit()

    return jsonify({
        "message": "Appointment created",
        "appointment": {
            "id": appointment.id,
            "patient_id": appointment.patient_id,
            "doctor_id": appointment.doctor_id,
            "date": appointment.appointment_date,
            "time": appointment.appointment_time,
            "status": appointment.status
        }
    }), 201


@app.route("/appointments/<int:appointment_id>", methods=["DELETE"])
def cancel_appointment(appointment_id):

    appointment = db.session.get(
        Appointment,
        appointment_id
    )

    if not appointment:

        return jsonify({
            "error": "Appointment not found"
        }), 404

    appointment.status = "cancelled"

    db.session.commit()

    return jsonify({
        "message": "Appointment cancelled",
        "appointment_id": appointment_id
    })


# =========================
# DATABASE INITIALIZATION
# =========================

with app.app_context():
    db.create_all()


# =========================
# START APPLICATION
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )