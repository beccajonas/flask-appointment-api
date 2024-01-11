#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime
from models import db, Doctor, Patient, Appointment

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.get("/")
def index():
    return "doctor/patient"

@app.get('/doctors')
def get_doctors():
    doctors = Doctor.query.all()
    return [d.to_dict(rules=['-appointments']) for d in doctors], 200

@app.get('/doctors/<int:id>')
def get_doctors_by_id(id):
    doctor = Doctor.query.filter_by(id=id).first()
    if not doctor:
        return {'error': 'not found'}
    return doctor.to_dict(rules=['-appointments.patient_id', '-appointments.doctor_id'])

@app.get('/patients/<int:id>')
def get_patient_by_id(id):
    patient = Patient.query.filter_by(id=id).first()
    patient_dict = patient.to_dict(rules=['-appointments'])
    doctors = [d.to_dict(rules=['-appointments']) for d in patient.doctors]
    patient_dict['doctors'] = doctors
    return patient_dict

@app.post('/doctors')
def post_doctors():
    try:
        data = request.json
        doctor = Doctor(name=data.get('name'), specialty=data.get('specialty'))
        db.session.add(doctor)
        db.session.commit()
        return doctor.to_dict(), 201
    except Exception as e:
        return {"Error": str(e)}
    
@app.patch('/patients/<int:id>')
def patch_patients(id):
    # any time user input use try/catch
    try:
        data = request.json
        patient = db.session.get(Patient, id)
        if not patient:
            return {"Error": "not foudn"}
        for key in data:
            setattr(patient, key, data[key])
        db.session.add(patient)
        db.session.commit()
        return patient.to_dict(rules=["-appointments"])
    
    except Exception as e:
        return {"Error": str(e)}
    
@app.post('/appointments')
def post_appointments():
    try:
        data = request.json
        appointment = Appointment(day=data.get('day'), patient_id=data.get('patient_id'), doctor_id=data.get('doctor_id'))
        db.session.add(appointment)
        db.session.commit()
        return appointment.to_dict(rules=['-patient_id', '-doctor_id'])
    except Exception as e:
        return {"Error": str(e)}
    
if __name__ == "__main__":
    app.run(port=5555, debug=True)
