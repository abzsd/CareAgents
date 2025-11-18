"""
Seed script to create sample doctors in the database
"""
import asyncio
import asyncpg
import os
import uuid
import json
from dotenv import load_dotenv

load_dotenv()

# Sample doctor data
SAMPLE_DOCTORS = [
    {
        "first_name": "Sarah",
        "last_name": "Johnson",
        "email": "sarah.johnson@hospital.com",
        "phone": "+1-555-0101",
        "specialization": "Cardiology",
        "sub_specializations": ["Interventional Cardiology", "Heart Failure"],
        "license_number": "MD-CA-123456",
        "license_state": "California",
        "qualifications": [
            {"degree": "MD", "institution": "Stanford Medical School", "year": 2005},
            {"degree": "Fellowship in Cardiology", "institution": "Mayo Clinic", "year": 2010}
        ],
        "years_of_experience": 15,
        "consultation_fee": 250.00,
        "availability": [
            {"day_of_week": "Monday", "start_time": "09:00", "end_time": "17:00"},
            {"day_of_week": "Tuesday", "start_time": "09:00", "end_time": "17:00"},
            {"day_of_week": "Wednesday", "start_time": "09:00", "end_time": "17:00"},
            {"day_of_week": "Thursday", "start_time": "09:00", "end_time": "17:00"},
        ],
        "languages_spoken": ["English", "Spanish"],
        "rating": 4.8,
        "total_patients_treated": 1500
    },
    {
        "first_name": "Michael",
        "last_name": "Chen",
        "email": "michael.chen@hospital.com",
        "phone": "+1-555-0102",
        "specialization": "Neurology",
        "sub_specializations": ["Epilepsy", "Movement Disorders"],
        "license_number": "MD-CA-234567",
        "license_state": "California",
        "qualifications": [
            {"degree": "MD", "institution": "Harvard Medical School", "year": 2008},
            {"degree": "Fellowship in Neurology", "institution": "Johns Hopkins", "year": 2012}
        ],
        "years_of_experience": 12,
        "consultation_fee": 275.00,
        "availability": [
            {"day_of_week": "Monday", "start_time": "10:00", "end_time": "18:00"},
            {"day_of_week": "Wednesday", "start_time": "10:00", "end_time": "18:00"},
            {"day_of_week": "Friday", "start_time": "10:00", "end_time": "18:00"},
        ],
        "languages_spoken": ["English", "Mandarin"],
        "rating": 4.9,
        "total_patients_treated": 1200
    },
    {
        "first_name": "Emily",
        "last_name": "Rodriguez",
        "email": "emily.rodriguez@hospital.com",
        "phone": "+1-555-0103",
        "specialization": "Pediatrics",
        "sub_specializations": ["Neonatology", "Developmental Pediatrics"],
        "license_number": "MD-CA-345678",
        "license_state": "California",
        "qualifications": [
            {"degree": "MD", "institution": "UCSF Medical School", "year": 2010},
            {"degree": "Fellowship in Pediatrics", "institution": "Children's Hospital Boston", "year": 2014}
        ],
        "years_of_experience": 10,
        "consultation_fee": 200.00,
        "availability": [
            {"day_of_week": "Monday", "start_time": "08:00", "end_time": "16:00"},
            {"day_of_week": "Tuesday", "start_time": "08:00", "end_time": "16:00"},
            {"day_of_week": "Thursday", "start_time": "08:00", "end_time": "16:00"},
            {"day_of_week": "Friday", "start_time": "08:00", "end_time": "14:00"},
        ],
        "languages_spoken": ["English", "Spanish", "Portuguese"],
        "rating": 4.7,
        "total_patients_treated": 2000
    },
    {
        "first_name": "David",
        "last_name": "Patel",
        "email": "david.patel@hospital.com",
        "phone": "+1-555-0104",
        "specialization": "Orthopedics",
        "sub_specializations": ["Sports Medicine", "Joint Replacement"],
        "license_number": "MD-CA-456789",
        "license_state": "California",
        "qualifications": [
            {"degree": "MD", "institution": "UCLA Medical School", "year": 2007},
            {"degree": "Fellowship in Orthopedic Surgery", "institution": "Cleveland Clinic", "year": 2013}
        ],
        "years_of_experience": 13,
        "consultation_fee": 300.00,
        "availability": [
            {"day_of_week": "Tuesday", "start_time": "09:00", "end_time": "17:00"},
            {"day_of_week": "Wednesday", "start_time": "09:00", "end_time": "17:00"},
            {"day_of_week": "Thursday", "start_time": "09:00", "end_time": "17:00"},
        ],
        "languages_spoken": ["English", "Hindi", "Gujarati"],
        "rating": 4.6,
        "total_patients_treated": 1800
    },
    {
        "first_name": "Lisa",
        "last_name": "Williams",
        "email": "lisa.williams@hospital.com",
        "phone": "+1-555-0105",
        "specialization": "Dermatology",
        "sub_specializations": ["Cosmetic Dermatology", "Skin Cancer"],
        "license_number": "MD-CA-567890",
        "license_state": "California",
        "qualifications": [
            {"degree": "MD", "institution": "USC Medical School", "year": 2009},
            {"degree": "Fellowship in Dermatology", "institution": "NYU Langone", "year": 2013}
        ],
        "years_of_experience": 11,
        "consultation_fee": 225.00,
        "availability": [
            {"day_of_week": "Monday", "start_time": "09:00", "end_time": "17:00"},
            {"day_of_week": "Tuesday", "start_time": "09:00", "end_time": "17:00"},
            {"day_of_week": "Wednesday", "start_time": "09:00", "end_time": "13:00"},
            {"day_of_week": "Friday", "start_time": "09:00", "end_time": "17:00"},
        ],
        "languages_spoken": ["English"],
        "rating": 4.9,
        "total_patients_treated": 2500
    },
    {
        "first_name": "James",
        "last_name": "Thompson",
        "email": "james.thompson@hospital.com",
        "phone": "+1-555-0106",
        "specialization": "General Practice",
        "sub_specializations": ["Family Medicine", "Preventive Care"],
        "license_number": "MD-CA-678901",
        "license_state": "California",
        "qualifications": [
            {"degree": "MD", "institution": "UC San Diego Medical School", "year": 2012},
            {"degree": "Residency in Family Medicine", "institution": "Kaiser Permanente", "year": 2015}
        ],
        "years_of_experience": 8,
        "consultation_fee": 150.00,
        "availability": [
            {"day_of_week": "Monday", "start_time": "08:00", "end_time": "18:00"},
            {"day_of_week": "Tuesday", "start_time": "08:00", "end_time": "18:00"},
            {"day_of_week": "Wednesday", "start_time": "08:00", "end_time": "18:00"},
            {"day_of_week": "Thursday", "start_time": "08:00", "end_time": "18:00"},
            {"day_of_week": "Friday", "start_time": "08:00", "end_time": "18:00"},
        ],
        "languages_spoken": ["English"],
        "rating": 4.5,
        "total_patients_treated": 3000
    },
    {
        "first_name": "Rachel",
        "last_name": "Kim",
        "email": "rachel.kim@hospital.com",
        "phone": "+1-555-0107",
        "specialization": "Psychiatry",
        "sub_specializations": ["Anxiety Disorders", "Depression", "ADHD"],
        "license_number": "MD-CA-789012",
        "license_state": "California",
        "qualifications": [
            {"degree": "MD", "institution": "Yale Medical School", "year": 2011},
            {"degree": "Residency in Psychiatry", "institution": "Massachusetts General Hospital", "year": 2015}
        ],
        "years_of_experience": 9,
        "consultation_fee": 280.00,
        "availability": [
            {"day_of_week": "Monday", "start_time": "10:00", "end_time": "19:00"},
            {"day_of_week": "Tuesday", "start_time": "10:00", "end_time": "19:00"},
            {"day_of_week": "Thursday", "start_time": "10:00", "end_time": "19:00"},
        ],
        "languages_spoken": ["English", "Korean"],
        "rating": 4.8,
        "total_patients_treated": 800
    },
    {
        "first_name": "Robert",
        "last_name": "Martinez",
        "email": "robert.martinez@hospital.com",
        "phone": "+1-555-0108",
        "specialization": "Gastroenterology",
        "sub_specializations": ["IBD", "Liver Diseases", "Endoscopy"],
        "license_number": "MD-CA-890123",
        "license_state": "California",
        "qualifications": [
            {"degree": "MD", "institution": "Columbia Medical School", "year": 2006},
            {"degree": "Fellowship in Gastroenterology", "institution": "University of Michigan", "year": 2011}
        ],
        "years_of_experience": 14,
        "consultation_fee": 260.00,
        "availability": [
            {"day_of_week": "Monday", "start_time": "09:00", "end_time": "17:00"},
            {"day_of_week": "Wednesday", "start_time": "09:00", "end_time": "17:00"},
            {"day_of_week": "Friday", "start_time": "09:00", "end_time": "17:00"},
        ],
        "languages_spoken": ["English", "Spanish"],
        "rating": 4.7,
        "total_patients_treated": 1600
    }
]


async def seed_doctors():
    """Seed the database with sample doctors"""

    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "5432"))
    db_name = os.getenv("DB_NAME", "healthcare_db")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")

    print(f"Connecting to PostgreSQL: {db_host}:{db_port}/{db_name}")

    try:
        pool = await asyncpg.create_pool(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password,
            min_size=1,
            max_size=5
        )

        print("✓ Connected to PostgreSQL")

        async with pool.acquire() as conn:
            existing_count = await conn.fetchval("SELECT COUNT(*) FROM doctors")
            print(f"Existing doctors in database: {existing_count}")

            if existing_count > 0:
                print("Deleting existing doctors...")
                await conn.execute("DELETE FROM doctors")
                print("✓ Deleted existing doctors")

        inserted_count = 0
        async with pool.acquire() as conn:
            for doctor_data in SAMPLE_DOCTORS:
                doctor_id = str(uuid.uuid4())

                await conn.execute("""
                    INSERT INTO doctors (
                        doctor_id, first_name, last_name, email, phone,
                        specialization, sub_specializations, license_number, license_state,
                        qualifications, years_of_experience, consultation_fee,
                        availability, languages_spoken, rating, total_patients_treated,
                        is_active, created_at, updated_at
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                """,
                    doctor_id,
                    doctor_data["first_name"],
                    doctor_data["last_name"],
                    doctor_data["email"],
                    doctor_data["phone"],
                    doctor_data["specialization"],
                    json.dumps(doctor_data["sub_specializations"]),
                    doctor_data["license_number"],
                    doctor_data["license_state"],
                    json.dumps(doctor_data["qualifications"]),
                    doctor_data["years_of_experience"],
                    doctor_data["consultation_fee"],
                    json.dumps(doctor_data["availability"]),
                    json.dumps(doctor_data["languages_spoken"]),
                    doctor_data["rating"],
                    doctor_data["total_patients_treated"],
                    True
                )

                inserted_count += 1
                print(f"✓ Inserted: Dr. {doctor_data['first_name']} {doctor_data['last_name']} - {doctor_data['specialization']}")

        print(f"\n✓ Successfully seeded {inserted_count} doctors")

        async with pool.acquire() as conn:
            total = await conn.fetchval("SELECT COUNT(*) FROM doctors")
            print(f"✓ Total doctors in database: {total}")

        await pool.close()
        print("✓ Database connection closed")

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(seed_doctors())
