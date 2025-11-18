"""
Comprehensive database seeding script for CareAgents Healthcare System
Seeds all tables with realistic sample data
"""
import asyncio
import asyncpg
import os
import uuid
import json
from datetime import date, datetime, timedelta, time
from dotenv import load_dotenv
import random

load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "healthcare_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}


async def seed_users(conn):
    """Seed users table with sample users"""
    print("\n🔹 Seeding users...")

    users = [
        {
            "user_id": str(uuid.uuid4()),
            "email": "dr.smith@healthcare.com",
            "display_name": "Dr. John Smith",
            "photo_url": "https://randomuser.me/api/portraits/men/1.jpg",
            "role": "doctor",
            "is_onboarded": True,
            "firebase_uid": f"firebase_{uuid.uuid4()}",
            "provider_id": "google.com",
            "last_login_at": datetime.now(),
            "is_active": True,
        },
        {
            "user_id": str(uuid.uuid4()),
            "email": "dr.johnson@healthcare.com",
            "display_name": "Dr. Emily Johnson",
            "photo_url": "https://randomuser.me/api/portraits/women/1.jpg",
            "role": "doctor",
            "is_onboarded": True,
            "firebase_uid": f"firebase_{uuid.uuid4()}",
            "provider_id": "google.com",
            "last_login_at": datetime.now(),
            "is_active": True,
        },
        {
            "user_id": str(uuid.uuid4()),
            "email": "patient1@email.com",
            "display_name": "John Doe",
            "photo_url": "https://randomuser.me/api/portraits/men/10.jpg",
            "role": "patient",
            "is_onboarded": True,
            "firebase_uid": f"firebase_{uuid.uuid4()}",
            "provider_id": "google.com",
            "last_login_at": datetime.now(),
            "is_active": True,
        },
        {
            "user_id": str(uuid.uuid4()),
            "email": "patient2@email.com",
            "display_name": "Jane Smith",
            "photo_url": "https://randomuser.me/api/portraits/women/10.jpg",
            "role": "patient",
            "is_onboarded": True,
            "firebase_uid": f"firebase_{uuid.uuid4()}",
            "provider_id": "google.com",
            "last_login_at": datetime.now(),
            "is_active": True,
        },
        {
            "user_id": str(uuid.uuid4()),
            "email": "admin@healthcare.com",
            "display_name": "Admin User",
            "photo_url": "https://randomuser.me/api/portraits/men/50.jpg",
            "role": "admin",
            "is_onboarded": True,
            "firebase_uid": f"firebase_{uuid.uuid4()}",
            "provider_id": "google.com",
            "last_login_at": datetime.now(),
            "is_active": True,
        },
    ]

    insert_query = """
        INSERT INTO users (
            user_id, email, display_name, photo_url, role, is_onboarded,
            firebase_uid, provider_id, last_login_at, is_active, created_at, updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
    """

    for user in users:
        await conn.execute(
            insert_query,
            user["user_id"],
            user["email"],
            user["display_name"],
            user["photo_url"],
            user["role"],
            user["is_onboarded"],
            user["firebase_uid"],
            user["provider_id"],
            user["last_login_at"],
            user["is_active"],
            datetime.now(),
            datetime.now(),
        )

    print(f"✅ Seeded {len(users)} users")
    return users


async def seed_patients(conn, users):
    """Seed patients table with sample patients"""
    print("\n🔹 Seeding patients...")

    patient_users = [u for u in users if u["role"] == "patient"]

    patients = [
        {
            "patient_id": str(uuid.uuid4()),
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": date(1985, 5, 15),
            "age": 39,
            "gender": "Male",
            "email": "patient1@email.com",
            "phone": "+1-555-0101",
            "address": {
                "street": "123 Main St",
                "city": "Boston",
                "state": "MA",
                "zip_code": "02101",
                "country": "USA"
            },
            "emergency_contact": {
                "name": "Sarah Doe",
                "relationship": "Spouse",
                "phone": "+1-555-0102"
            },
            "blood_type": "O+",
            "allergies": ["Penicillin", "Peanuts"],
            "chronic_conditions": ["Hypertension"],
            "insurance_info": {
                "provider": "Blue Cross Blue Shield",
                "policy_number": "BCBS123456",
                "group_number": "GRP789"
            }
        },
        {
            "patient_id": str(uuid.uuid4()),
            "first_name": "Jane",
            "last_name": "Smith",
            "date_of_birth": date(1990, 8, 22),
            "age": 34,
            "gender": "Female",
            "email": "patient2@email.com",
            "phone": "+1-555-0201",
            "address": {
                "street": "456 Oak Ave",
                "city": "Cambridge",
                "state": "MA",
                "zip_code": "02138",
                "country": "USA"
            },
            "emergency_contact": {
                "name": "Michael Smith",
                "relationship": "Brother",
                "phone": "+1-555-0202"
            },
            "blood_type": "A+",
            "allergies": ["Latex"],
            "chronic_conditions": ["Diabetes Type 2"],
            "insurance_info": {
                "provider": "Aetna",
                "policy_number": "AET987654",
                "group_number": "GRP321"
            }
        },
        {
            "patient_id": str(uuid.uuid4()),
            "first_name": "Robert",
            "last_name": "Johnson",
            "date_of_birth": date(1975, 3, 10),
            "age": 49,
            "gender": "Male",
            "email": "robert.j@email.com",
            "phone": "+1-555-0301",
            "address": {
                "street": "789 Elm St",
                "city": "Somerville",
                "state": "MA",
                "zip_code": "02144",
                "country": "USA"
            },
            "emergency_contact": {
                "name": "Lisa Johnson",
                "relationship": "Spouse",
                "phone": "+1-555-0302"
            },
            "blood_type": "B+",
            "allergies": [],
            "chronic_conditions": ["High Cholesterol", "Arthritis"],
            "insurance_info": {
                "provider": "UnitedHealthcare",
                "policy_number": "UHC456789",
                "group_number": "GRP654"
            }
        },
        {
            "patient_id": str(uuid.uuid4()),
            "first_name": "Maria",
            "last_name": "Garcia",
            "date_of_birth": date(1995, 11, 5),
            "age": 29,
            "gender": "Female",
            "email": "maria.g@email.com",
            "phone": "+1-555-0401",
            "address": {
                "street": "321 Pine St",
                "city": "Brookline",
                "state": "MA",
                "zip_code": "02445",
                "country": "USA"
            },
            "emergency_contact": {
                "name": "Carlos Garcia",
                "relationship": "Father",
                "phone": "+1-555-0402"
            },
            "blood_type": "AB+",
            "allergies": ["Shellfish"],
            "chronic_conditions": [],
            "insurance_info": {
                "provider": "Cigna",
                "policy_number": "CIG123789",
                "group_number": "GRP987"
            }
        },
        {
            "patient_id": str(uuid.uuid4()),
            "first_name": "David",
            "last_name": "Wilson",
            "date_of_birth": date(1982, 7, 18),
            "age": 42,
            "gender": "Male",
            "email": "david.w@email.com",
            "phone": "+1-555-0501",
            "address": {
                "street": "654 Maple Dr",
                "city": "Newton",
                "state": "MA",
                "zip_code": "02458",
                "country": "USA"
            },
            "emergency_contact": {
                "name": "Emily Wilson",
                "relationship": "Spouse",
                "phone": "+1-555-0502"
            },
            "blood_type": "O-",
            "allergies": ["Sulfa drugs"],
            "chronic_conditions": ["Asthma"],
            "insurance_info": {
                "provider": "Humana",
                "policy_number": "HUM789456",
                "group_number": "GRP147"
            }
        },
    ]

    insert_query = """
        INSERT INTO patients (
            patient_id, first_name, last_name, date_of_birth, age, gender,
            email, phone, address, emergency_contact, blood_type, allergies,
            chronic_conditions, insurance_info, is_active, created_at, updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
    """

    for patient in patients:
        await conn.execute(
            insert_query,
            patient["patient_id"],
            patient["first_name"],
            patient["last_name"],
            patient["date_of_birth"],
            patient["age"],
            patient["gender"],
            patient["email"],
            patient["phone"],
            json.dumps(patient["address"]),
            json.dumps(patient["emergency_contact"]),
            patient["blood_type"],
            json.dumps(patient["allergies"]),
            json.dumps(patient["chronic_conditions"]),
            json.dumps(patient["insurance_info"]),
            True,
            datetime.now(),
            datetime.now(),
        )

    print(f"✅ Seeded {len(patients)} patients")
    return patients


async def seed_doctors(conn, users):
    """Seed doctors table with sample doctors"""
    print("\n🔹 Seeding doctors...")

    doctor_users = [u for u in users if u["role"] == "doctor"]

    doctors = [
        {
            "doctor_id": str(uuid.uuid4()),
            "user_id": doctor_users[0]["user_id"] if len(doctor_users) > 0 else None,
            "first_name": "John",
            "last_name": "Smith",
            "email": "dr.smith@healthcare.com",
            "phone": "+1-555-1001",
            "specialization": "Cardiology",
            "sub_specializations": ["Interventional Cardiology", "Heart Failure"],
            "license_number": "MD123456",
            "license_state": "Massachusetts",
            "qualifications": [
                {"degree": "MD", "institution": "Harvard Medical School", "year": 2005},
                {"degree": "Fellowship", "institution": "Mayo Clinic", "year": 2010}
            ],
            "years_of_experience": 15,
            "consultation_fee": 250.00,
            "availability": [
                {"day_of_week": "Monday", "start_time": "09:00", "end_time": "17:00"},
                {"day_of_week": "Wednesday", "start_time": "09:00", "end_time": "17:00"},
                {"day_of_week": "Friday", "start_time": "09:00", "end_time": "13:00"}
            ],
            "languages_spoken": ["English", "Spanish"],
            "rating": 4.8,
            "total_patients_treated": 1250,
            "address": {
                "street": "100 Medical Plaza",
                "city": "Boston",
                "state": "MA",
                "zip_code": "02115",
                "country": "USA"
            },
            "certifications": ["Board Certified in Cardiology", "ACLS Certified"]
        },
        {
            "doctor_id": str(uuid.uuid4()),
            "user_id": doctor_users[1]["user_id"] if len(doctor_users) > 1 else None,
            "first_name": "Emily",
            "last_name": "Johnson",
            "email": "dr.johnson@healthcare.com",
            "phone": "+1-555-1002",
            "specialization": "Pediatrics",
            "sub_specializations": ["Adolescent Medicine", "Preventive Care"],
            "license_number": "MD789012",
            "license_state": "Massachusetts",
            "qualifications": [
                {"degree": "MD", "institution": "Johns Hopkins University", "year": 2008},
                {"degree": "Residency", "institution": "Boston Children's Hospital", "year": 2012}
            ],
            "years_of_experience": 12,
            "consultation_fee": 180.00,
            "availability": [
                {"day_of_week": "Tuesday", "start_time": "08:00", "end_time": "16:00"},
                {"day_of_week": "Thursday", "start_time": "08:00", "end_time": "16:00"},
                {"day_of_week": "Saturday", "start_time": "09:00", "end_time": "12:00"}
            ],
            "languages_spoken": ["English", "French"],
            "rating": 4.9,
            "total_patients_treated": 980,
            "address": {
                "street": "200 Children's Way",
                "city": "Cambridge",
                "state": "MA",
                "zip_code": "02139",
                "country": "USA"
            },
            "certifications": ["Board Certified in Pediatrics", "PALS Certified"]
        },
        {
            "doctor_id": str(uuid.uuid4()),
            "user_id": None,
            "first_name": "Michael",
            "last_name": "Chen",
            "email": "dr.chen@healthcare.com",
            "phone": "+1-555-1003",
            "specialization": "Neurology",
            "sub_specializations": ["Stroke Care", "Epilepsy"],
            "license_number": "MD345678",
            "license_state": "Massachusetts",
            "qualifications": [
                {"degree": "MD", "institution": "Stanford University", "year": 2006},
                {"degree": "Fellowship", "institution": "Cleveland Clinic", "year": 2012}
            ],
            "years_of_experience": 13,
            "consultation_fee": 300.00,
            "availability": [
                {"day_of_week": "Monday", "start_time": "10:00", "end_time": "18:00"},
                {"day_of_week": "Wednesday", "start_time": "10:00", "end_time": "18:00"}
            ],
            "languages_spoken": ["English", "Mandarin"],
            "rating": 4.7,
            "total_patients_treated": 850,
            "address": {
                "street": "300 Neuroscience Center",
                "city": "Boston",
                "state": "MA",
                "zip_code": "02114",
                "country": "USA"
            },
            "certifications": ["Board Certified in Neurology", "Stroke Specialist"]
        },
    ]

    insert_query = """
        INSERT INTO doctors (
            doctor_id, user_id, first_name, last_name, email, phone,
            specialization, sub_specializations, license_number, license_state,
            qualifications, years_of_experience, consultation_fee, availability,
            languages_spoken, rating, total_patients_treated, address, certifications,
            is_active, created_at, updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22)
    """

    for doctor in doctors:
        await conn.execute(
            insert_query,
            doctor["doctor_id"],
            doctor["user_id"],
            doctor["first_name"],
            doctor["last_name"],
            doctor["email"],
            doctor["phone"],
            doctor["specialization"],
            json.dumps(doctor["sub_specializations"]),
            doctor["license_number"],
            doctor["license_state"],
            json.dumps(doctor["qualifications"]),
            doctor["years_of_experience"],
            doctor["consultation_fee"],
            json.dumps(doctor["availability"]),
            json.dumps(doctor["languages_spoken"]),
            doctor["rating"],
            doctor["total_patients_treated"],
            json.dumps(doctor["address"]),
            json.dumps(doctor["certifications"]),
            True,
            datetime.now(),
            datetime.now(),
        )

    print(f"✅ Seeded {len(doctors)} doctors")
    return doctors


async def seed_appointments(conn, patients, doctors):
    """Seed appointments table with sample appointments"""
    print("\n🔹 Seeding appointments...")

    appointments = []
    statuses = ["scheduled", "confirmed", "completed", "cancelled"]
    appointment_types = ["consultation", "follow_up", "routine_checkup", "emergency"]

    # Create appointments for the next 30 days and past 60 days
    for i in range(20):
        patient = random.choice(patients)
        doctor = random.choice(doctors)

        # Mix of past and future appointments
        if i < 10:
            # Past appointments
            days_ago = random.randint(1, 60)
            appointment_date = date.today() - timedelta(days=days_ago)
            status = random.choice(["completed", "cancelled", "no_show"])
        else:
            # Future appointments
            days_ahead = random.randint(1, 30)
            appointment_date = date.today() + timedelta(days=days_ahead)
            status = random.choice(["scheduled", "confirmed"])

        appointment = {
            "appointment_id": str(uuid.uuid4()),
            "patient_id": patient["patient_id"],
            "doctor_id": doctor["doctor_id"],
            "appointment_date": appointment_date,
            "appointment_time": time(random.randint(9, 16), 0, 0),
            "appointment_type": random.choice(appointment_types),
            "status": status,
            "reason": random.choice([
                "Annual checkup",
                "Follow-up consultation",
                "New symptoms evaluation",
                "Medication review",
                "Routine physical examination"
            ]),
            "notes": "Patient arrived on time" if status == "completed" else None,
            "location": f"{doctor['address']['street']}, {doctor['address']['city']}",
            "duration_minutes": random.choice([30, 45, 60])
        }
        appointments.append(appointment)

    insert_query = """
        INSERT INTO appointments (
            appointment_id, patient_id, doctor_id, appointment_date, appointment_time,
            appointment_type, status, reason, notes, location, duration_minutes,
            is_active, created_at, updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
    """

    for appointment in appointments:
        await conn.execute(
            insert_query,
            appointment["appointment_id"],
            appointment["patient_id"],
            appointment["doctor_id"],
            appointment["appointment_date"],
            appointment["appointment_time"],
            appointment["appointment_type"],
            appointment["status"],
            appointment["reason"],
            appointment["notes"],
            appointment["location"],
            appointment["duration_minutes"],
            True,
            datetime.now(),
            datetime.now(),
        )

    print(f"✅ Seeded {len(appointments)} appointments")
    return appointments


async def seed_medical_history(conn, patients, doctors):
    """Seed medical history table with sample records"""
    print("\n🔹 Seeding medical history...")

    medical_histories = []
    diagnoses = [
        "Hypertension - well controlled",
        "Type 2 Diabetes - monitoring blood glucose",
        "Upper respiratory infection",
        "Seasonal allergies",
        "Migraine headaches",
        "Lower back pain - muscular",
        "Anxiety disorder",
        "Gastroesophageal reflux disease"
    ]

    for i in range(15):
        patient = random.choice(patients)
        doctor = random.choice(doctors)
        days_ago = random.randint(1, 180)
        visit_date = date.today() - timedelta(days=days_ago)

        history = {
            "history_id": str(uuid.uuid4()),
            "patient_id": patient["patient_id"],
            "doctor_id": doctor["doctor_id"],
            "doctor_name": f"Dr. {doctor['first_name']} {doctor['last_name']}",
            "visit_date": visit_date,
            "diagnosis": random.choice(diagnoses),
            "prescriptions": [
                {
                    "medication_name": random.choice(["Lisinopril", "Metformin", "Amoxicillin", "Ibuprofen"]),
                    "dosage": random.choice(["10mg", "500mg", "250mg", "200mg"]),
                    "frequency": random.choice(["Once daily", "Twice daily", "Three times daily"]),
                    "duration": random.choice(["30 days", "60 days", "90 days"]),
                    "instructions": "Take with food"
                }
            ],
            "health_status": random.choice(["Stable", "Improving", "Requires monitoring"]),
            "blood_pressure": f"{random.randint(110, 140)}/{random.randint(70, 90)}",
            "symptoms": random.sample(["Headache", "Fatigue", "Cough", "Fever", "Chest pain"], k=random.randint(1, 3)),
            "notes": "Patient is responding well to treatment. Continue current medication regimen.",
            "follow_up_date": visit_date + timedelta(days=random.randint(30, 90))
        }
        medical_histories.append(history)

    insert_query = """
        INSERT INTO medical_history (
            history_id, patient_id, doctor_id, doctor_name, visit_date,
            diagnosis, prescriptions, health_status, blood_pressure, symptoms,
            notes, follow_up_date, is_active, created_at, updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
    """

    for history in medical_histories:
        await conn.execute(
            insert_query,
            history["history_id"],
            history["patient_id"],
            history["doctor_id"],
            history["doctor_name"],
            history["visit_date"],
            history["diagnosis"],
            json.dumps(history["prescriptions"]),
            history["health_status"],
            history["blood_pressure"],
            json.dumps(history["symptoms"]),
            history["notes"],
            history["follow_up_date"],
            True,
            datetime.now(),
            datetime.now(),
        )

    print(f"✅ Seeded {len(medical_histories)} medical history records")
    return medical_histories


async def seed_health_vitals(conn, patients, users):
    """Seed health vitals table with sample vital records"""
    print("\n🔹 Seeding health vitals...")

    vitals = []
    vital_types = [
        ("blood_pressure", "120/80", "mmHg"),
        ("heart_rate", "72", "bpm"),
        ("temperature", "98.6", "°F"),
        ("weight", "165", "lbs"),
        ("height", "68", "inches"),
        ("oxygen_saturation", "98", "%"),
        ("blood_glucose", "95", "mg/dL"),
    ]

    # Create multiple vital readings for each patient over time
    for patient in patients[:3]:  # Just for first 3 patients to keep it manageable
        for days_ago in [1, 7, 14, 30, 60]:
            recorded_at = datetime.now() - timedelta(days=days_ago)

            for vital_type, base_value, unit in vital_types:
                # Add some variation to values
                if vital_type == "blood_pressure":
                    value = base_value
                elif vital_type == "weight":
                    value = str(float(base_value) + random.uniform(-5, 5))
                elif vital_type == "blood_glucose":
                    value = str(int(base_value) + random.randint(-10, 20))
                else:
                    value = str(float(base_value) + random.uniform(-2, 2))

                vital = {
                    "vital_id": str(uuid.uuid4()),
                    "patient_id": patient["patient_id"],
                    "recorded_by": users[0]["user_id"],  # Recorded by first user (admin/doctor)
                    "vital_type": vital_type,
                    "value": value if vital_type == "blood_pressure" else float(value),
                    "unit": unit,
                    "recorded_at": recorded_at,
                    "notes": "Routine vital check" if days_ago > 7 else "Recent check"
                }
                vitals.append(vital)

    insert_query = """
        INSERT INTO health_vitals (
            vital_id, patient_id, recorded_by, vital_type, value, unit,
            recorded_at, notes, is_active, created_at, updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
    """

    for vital in vitals:
        # Handle blood_pressure differently as it's a string
        value_to_insert = vital["value"] if vital["vital_type"] == "blood_pressure" else str(vital["value"])

        await conn.execute(
            insert_query,
            vital["vital_id"],
            vital["patient_id"],
            vital["recorded_by"],
            vital["vital_type"],
            value_to_insert,
            vital["unit"],
            vital["recorded_at"],
            vital["notes"],
            True,
            datetime.now(),
            datetime.now(),
        )

    print(f"✅ Seeded {len(vitals)} health vital records")
    return vitals


async def seed_prescriptions(conn, patients, doctors):
    """Seed prescriptions table with sample prescriptions"""
    print("\n🔹 Seeding prescriptions...")

    prescriptions = []

    for i in range(10):
        patient = random.choice(patients)
        doctor = random.choice(doctors)
        days_ago = random.randint(1, 90)
        prescribed_date = date.today() - timedelta(days=days_ago)

        prescription = {
            "prescription_id": str(uuid.uuid4()),
            "patient_id": patient["patient_id"],
            "doctor_id": doctor["doctor_id"],
            "medications": [
                {
                    "name": random.choice(["Lisinopril", "Metformin", "Atorvastatin", "Omeprazole"]),
                    "dosage": random.choice(["10mg", "20mg", "500mg", "1000mg"]),
                    "frequency": random.choice(["Once daily", "Twice daily", "Three times daily"]),
                    "duration": random.choice(["30 days", "60 days", "90 days"]),
                    "instructions": random.choice(["Take with food", "Take on empty stomach", "Take before bedtime"])
                },
                {
                    "name": random.choice(["Aspirin", "Vitamin D", "Calcium", "Multivitamin"]),
                    "dosage": random.choice(["81mg", "1000IU", "500mg", "1 tablet"]),
                    "frequency": "Once daily",
                    "duration": "90 days",
                    "instructions": "Take with breakfast"
                }
            ],
            "diagnosis": random.choice([
                "Hypertension",
                "Type 2 Diabetes",
                "High Cholesterol",
                "GERD",
                "Preventive Care"
            ]),
            "notes": "Follow up in 30 days to assess medication effectiveness",
            "prescribed_date": prescribed_date,
            "valid_until": prescribed_date + timedelta(days=90)
        }
        prescriptions.append(prescription)

    insert_query = """
        INSERT INTO prescriptions (
            prescription_id, patient_id, doctor_id, medications, diagnosis,
            notes, prescribed_date, valid_until, is_active, created_at, updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
    """

    for prescription in prescriptions:
        await conn.execute(
            insert_query,
            prescription["prescription_id"],
            prescription["patient_id"],
            prescription["doctor_id"],
            json.dumps(prescription["medications"]),
            prescription["diagnosis"],
            prescription["notes"],
            prescription["prescribed_date"],
            prescription["valid_until"],
            True,
            datetime.now(),
            datetime.now(),
        )

    print(f"✅ Seeded {len(prescriptions)} prescriptions")
    return prescriptions


async def seed_medical_reports(conn, patients, doctors):
    """Seed medical reports table with sample reports"""
    print("\n🔹 Seeding medical reports...")

    reports = []
    report_types = ["Lab Results", "X-Ray", "MRI Scan", "CT Scan", "Blood Test", "Urine Analysis", "ECG"]

    for i in range(12):
        patient = random.choice(patients)
        doctor = random.choice(doctors)
        days_ago = random.randint(1, 120)
        report_date = date.today() - timedelta(days=days_ago)
        report_type = random.choice(report_types)

        report = {
            "report_id": str(uuid.uuid4()),
            "patient_id": patient["patient_id"],
            "doctor_id": doctor["doctor_id"],
            "report_type": report_type,
            "title": f"{report_type} - {report_date.strftime('%B %Y')}",
            "content": f"Report findings for {report_type}: Results are within normal range. No significant abnormalities detected.",
            "file_url": f"https://storage.googleapis.com/healthcare-reports/{uuid.uuid4()}.pdf",
            "report_date": report_date
        }
        reports.append(report)

    insert_query = """
        INSERT INTO medical_reports (
            report_id, patient_id, doctor_id, report_type, title, content,
            file_url, report_date, is_active, created_at, updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
    """

    for report in reports:
        await conn.execute(
            insert_query,
            report["report_id"],
            report["patient_id"],
            report["doctor_id"],
            report["report_type"],
            report["title"],
            report["content"],
            report["file_url"],
            report["report_date"],
            True,
            datetime.now(),
            datetime.now(),
        )

    print(f"✅ Seeded {len(reports)} medical reports")
    return reports


async def main():
    """Main seeding function"""
    print("=" * 60)
    print("🌱 Starting Database Seeding for CareAgents Healthcare System")
    print("=" * 60)

    try:
        # Connect to database
        print("\n🔌 Connecting to database...")
        conn = await asyncpg.connect(**DB_CONFIG)
        print("✅ Connected successfully!")

        # Clear all tables in reverse order (respecting foreign key constraints)
        print("\n🗑️  Clearing existing data...")
        await conn.execute("DELETE FROM medical_reports")
        await conn.execute("DELETE FROM prescriptions")
        await conn.execute("DELETE FROM health_vitals")
        await conn.execute("DELETE FROM medical_history")
        await conn.execute("DELETE FROM appointments")
        await conn.execute("DELETE FROM doctors")
        await conn.execute("DELETE FROM patients")
        await conn.execute("DELETE FROM users")
        print("✅ Existing data cleared")

        # Seed all tables in order (respecting foreign key constraints)
        users = await seed_users(conn)
        patients = await seed_patients(conn, users)
        doctors = await seed_doctors(conn, users)
        appointments = await seed_appointments(conn, patients, doctors)
        medical_histories = await seed_medical_history(conn, patients, doctors)
        health_vitals = await seed_health_vitals(conn, patients, users)
        prescriptions = await seed_prescriptions(conn, patients, doctors)
        medical_reports = await seed_medical_reports(conn, patients, doctors)

        # Summary
        print("\n" + "=" * 60)
        print("✨ Database Seeding Completed Successfully!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"   • Users: {len(users)}")
        print(f"   • Patients: {len(patients)}")
        print(f"   • Doctors: {len(doctors)}")
        print(f"   • Appointments: {len(appointments)}")
        print(f"   • Medical Histories: {len(medical_histories)}")
        print(f"   • Health Vitals: {len(health_vitals)}")
        print(f"   • Prescriptions: {len(prescriptions)}")
        print(f"   • Medical Reports: {len(medical_reports)}")
        print(f"\n🎉 Total records created: {len(users) + len(patients) + len(doctors) + len(appointments) + len(medical_histories) + len(health_vitals) + len(prescriptions) + len(medical_reports)}")

        # Close connection
        await conn.close()
        print("\n🔌 Database connection closed")

    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(main())
