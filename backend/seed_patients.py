"""
Seed script to create sample patients in the database
"""
import asyncio
import asyncpg
import os
import uuid
import json
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

# Sample patient data
SAMPLE_PATIENTS = [
    {
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1985-03-15",
        "gender": "Male",
        "email": "john.doe@email.com",
        "phone": "+1-555-1001",
        "address": {
            "street": "123 Main St",
            "city": "Los Angeles",
            "state": "CA",
            "zip_code": "90001",
            "country": "USA"
        },
        "emergency_contact": {
            "name": "Jane Doe",
            "relationship": "Spouse",
            "phone": "+1-555-1002"
        },
        "blood_type": "A+",
        "allergies": ["Penicillin", "Peanuts"],
        "chronic_conditions": ["Type 2 Diabetes", "Hypertension"],
        "insurance_info": {
            "provider": "Blue Cross Blue Shield",
            "policy_number": "BCBS123456",
            "group_number": "GRP001"
        }
    },
    {
        "first_name": "Maria",
        "last_name": "Garcia",
        "date_of_birth": "1990-07-22",
        "gender": "Female",
        "email": "maria.garcia@email.com",
        "phone": "+1-555-1003",
        "address": {
            "street": "456 Oak Ave",
            "city": "San Francisco",
            "state": "CA",
            "zip_code": "94102",
            "country": "USA"
        },
        "emergency_contact": {
            "name": "Carlos Garcia",
            "relationship": "Brother",
            "phone": "+1-555-1004"
        },
        "blood_type": "O+",
        "allergies": ["Latex"],
        "chronic_conditions": [],
        "insurance_info": {
            "provider": "Aetna",
            "policy_number": "AET789012",
            "group_number": "GRP002"
        }
    },
    {
        "first_name": "Robert",
        "last_name": "Smith",
        "date_of_birth": "1978-11-30",
        "gender": "Male",
        "email": "robert.smith@email.com",
        "phone": "+1-555-1005",
        "address": {
            "street": "789 Pine St",
            "city": "San Diego",
            "state": "CA",
            "zip_code": "92101",
            "country": "USA"
        },
        "emergency_contact": {
            "name": "Sarah Smith",
            "relationship": "Wife",
            "phone": "+1-555-1006"
        },
        "blood_type": "B+",
        "allergies": ["Sulfa drugs"],
        "chronic_conditions": ["Asthma", "High Cholesterol"],
        "insurance_info": {
            "provider": "Cigna",
            "policy_number": "CIG345678",
            "group_number": "GRP003"
        }
    },
    {
        "first_name": "Emily",
        "last_name": "Chen",
        "date_of_birth": "1995-02-14",
        "gender": "Female",
        "email": "emily.chen@email.com",
        "phone": "+1-555-1007",
        "address": {
            "street": "321 Elm St",
            "city": "Sacramento",
            "state": "CA",
            "zip_code": "95814",
            "country": "USA"
        },
        "emergency_contact": {
            "name": "David Chen",
            "relationship": "Father",
            "phone": "+1-555-1008"
        },
        "blood_type": "AB+",
        "allergies": [],
        "chronic_conditions": [],
        "insurance_info": {
            "provider": "Kaiser Permanente",
            "policy_number": "KP901234",
            "group_number": "GRP004"
        }
    },
    {
        "first_name": "Michael",
        "last_name": "Johnson",
        "date_of_birth": "1982-09-05",
        "gender": "Male",
        "email": "michael.johnson@email.com",
        "phone": "+1-555-1009",
        "address": {
            "street": "654 Maple Dr",
            "city": "Oakland",
            "state": "CA",
            "zip_code": "94601",
            "country": "USA"
        },
        "emergency_contact": {
            "name": "Lisa Johnson",
            "relationship": "Sister",
            "phone": "+1-555-1010"
        },
        "blood_type": "O-",
        "allergies": ["Iodine", "Shellfish"],
        "chronic_conditions": ["GERD"],
        "insurance_info": {
            "provider": "United Healthcare",
            "policy_number": "UHC567890",
            "group_number": "GRP005"
        }
    },
    {
        "first_name": "Sarah",
        "last_name": "Williams",
        "date_of_birth": "1988-12-18",
        "gender": "Female",
        "email": "sarah.williams@email.com",
        "phone": "+1-555-1011",
        "address": {
            "street": "987 Cedar Ln",
            "city": "San Jose",
            "state": "CA",
            "zip_code": "95101",
            "country": "USA"
        },
        "emergency_contact": {
            "name": "Tom Williams",
            "relationship": "Husband",
            "phone": "+1-555-1012"
        },
        "blood_type": "A-",
        "allergies": ["Aspirin"],
        "chronic_conditions": ["Migraine", "Anxiety"],
        "insurance_info": {
            "provider": "Blue Shield",
            "policy_number": "BS234567",
            "group_number": "GRP006"
        }
    },
    {
        "first_name": "David",
        "last_name": "Lee",
        "date_of_birth": "1975-06-28",
        "gender": "Male",
        "email": "david.lee@email.com",
        "phone": "+1-555-1013",
        "address": {
            "street": "147 Birch Ave",
            "city": "Fresno",
            "state": "CA",
            "zip_code": "93701",
            "country": "USA"
        },
        "emergency_contact": {
            "name": "Jennifer Lee",
            "relationship": "Wife",
            "phone": "+1-555-1014"
        },
        "blood_type": "B-",
        "allergies": ["Codeine"],
        "chronic_conditions": ["Arthritis", "Type 2 Diabetes"],
        "insurance_info": {
            "provider": "Humana",
            "policy_number": "HUM890123",
            "group_number": "GRP007"
        }
    },
    {
        "first_name": "Jessica",
        "last_name": "Brown",
        "date_of_birth": "1992-04-10",
        "gender": "Female",
        "email": "jessica.brown@email.com",
        "phone": "+1-555-1015",
        "address": {
            "street": "258 Spruce St",
            "city": "Long Beach",
            "state": "CA",
            "zip_code": "90801",
            "country": "USA"
        },
        "emergency_contact": {
            "name": "Mark Brown",
            "relationship": "Father",
            "phone": "+1-555-1016"
        },
        "blood_type": "O+",
        "allergies": [],
        "chronic_conditions": [],
        "insurance_info": {
            "provider": "Anthem",
            "policy_number": "ANT456789",
            "group_number": "GRP008"
        }
    },
    {
        "first_name": "Christopher",
        "last_name": "Martinez",
        "date_of_birth": "1980-08-25",
        "gender": "Male",
        "email": "chris.martinez@email.com",
        "phone": "+1-555-1017",
        "address": {
            "street": "369 Willow Rd",
            "city": "Anaheim",
            "state": "CA",
            "zip_code": "92801",
            "country": "USA"
        },
        "emergency_contact": {
            "name": "Maria Martinez",
            "relationship": "Mother",
            "phone": "+1-555-1018"
        },
        "blood_type": "AB-",
        "allergies": ["Penicillin", "Eggs"],
        "chronic_conditions": ["Sleep Apnea"],
        "insurance_info": {
            "provider": "Health Net",
            "policy_number": "HN012345",
            "group_number": "GRP009"
        }
    },
    {
        "first_name": "Amanda",
        "last_name": "Taylor",
        "date_of_birth": "1987-01-12",
        "gender": "Female",
        "email": "amanda.taylor@email.com",
        "phone": "+1-555-1019",
        "address": {
            "street": "741 Redwood Ave",
            "city": "Riverside",
            "state": "CA",
            "zip_code": "92501",
            "country": "USA"
        },
        "emergency_contact": {
            "name": "Kevin Taylor",
            "relationship": "Brother",
            "phone": "+1-555-1020"
        },
        "blood_type": "A+",
        "allergies": ["Morphine"],
        "chronic_conditions": ["Hypothyroidism"],
        "insurance_info": {
            "provider": "Oscar Health",
            "policy_number": "OSC678901",
            "group_number": "GRP010"
        }
    },
    {
        "first_name": "Daniel",
        "last_name": "Anderson",
        "date_of_birth": "1993-10-08",
        "gender": "Male",
        "email": "daniel.anderson@email.com",
        "phone": "+1-555-1021",
        "address": {
            "street": "852 Ash St",
            "city": "Santa Ana",
            "state": "CA",
            "zip_code": "92701",
            "country": "USA"
        },
        "emergency_contact": {
            "name": "Rebecca Anderson",
            "relationship": "Sister",
            "phone": "+1-555-1022"
        },
        "blood_type": "O+",
        "allergies": [],
        "chronic_conditions": [],
        "insurance_info": {
            "provider": "Blue Cross",
            "policy_number": "BC234567",
            "group_number": "GRP011"
        }
    },
    {
        "first_name": "Lisa",
        "last_name": "Thompson",
        "date_of_birth": "1976-05-20",
        "gender": "Female",
        "email": "lisa.thompson@email.com",
        "phone": "+1-555-1023",
        "address": {
            "street": "963 Walnut Blvd",
            "city": "Irvine",
            "state": "CA",
            "zip_code": "92602",
            "country": "USA"
        },
        "emergency_contact": {
            "name": "James Thompson",
            "relationship": "Husband",
            "phone": "+1-555-1024"
        },
        "blood_type": "B+",
        "allergies": ["NSAIDs", "Latex"],
        "chronic_conditions": ["Fibromyalgia", "Depression"],
        "insurance_info": {
            "provider": "Molina Healthcare",
            "policy_number": "MOL890123",
            "group_number": "GRP012"
        }
    },
    {
        "first_name": "Kevin",
        "last_name": "White",
        "date_of_birth": "1989-03-03",
        "gender": "Male",
        "email": "kevin.white@email.com",
        "phone": "+1-555-1025",
        "address": {
            "street": "159 Hickory Ct",
            "city": "Stockton",
            "state": "CA",
            "zip_code": "95201",
            "country": "USA"
        },
        "emergency_contact": {
            "name": "Rachel White",
            "relationship": "Wife",
            "phone": "+1-555-1026"
        },
        "blood_type": "A-",
        "allergies": ["Gluten"],
        "chronic_conditions": ["Celiac Disease"],
        "insurance_info": {
            "provider": "LA Care",
            "policy_number": "LAC456789",
            "group_number": "GRP013"
        }
    },
    {
        "first_name": "Rachel",
        "last_name": "Harris",
        "date_of_birth": "1991-11-16",
        "gender": "Female",
        "email": "rachel.harris@email.com",
        "phone": "+1-555-1027",
        "address": {
            "street": "753 Sycamore Dr",
            "city": "Fremont",
            "state": "CA",
            "zip_code": "94536",
            "country": "USA"
        },
        "emergency_contact": {
            "name": "Brian Harris",
            "relationship": "Father",
            "phone": "+1-555-1028"
        },
        "blood_type": "O-",
        "allergies": [],
        "chronic_conditions": [],
        "insurance_info": {
            "provider": "Covered California",
            "policy_number": "CC012345",
            "group_number": "GRP014"
        }
    },
    {
        "first_name": "Thomas",
        "last_name": "Clark",
        "date_of_birth": "1983-07-07",
        "gender": "Male",
        "email": "thomas.clark@email.com",
        "phone": "+1-555-1029",
        "address": {
            "street": "357 Poplar Ave",
            "city": "Modesto",
            "state": "CA",
            "zip_code": "95350",
            "country": "USA"
        },
        "emergency_contact": {
            "name": "Nancy Clark",
            "relationship": "Mother",
            "phone": "+1-555-1030"
        },
        "blood_type": "AB+",
        "allergies": ["Contrast dye"],
        "chronic_conditions": ["Chronic Kidney Disease"],
        "insurance_info": {
            "provider": "Medicare",
            "policy_number": "MED678901",
            "group_number": "GRP015"
        }
    }
]


async def seed_patients():
    """Seed the database with sample patients"""

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
            existing_count = await conn.fetchval("SELECT COUNT(*) FROM patients")
            print(f"Existing patients in database: {existing_count}")

            if existing_count > 0:
                print("Deleting existing patients...")
                await conn.execute("DELETE FROM patients")
                print("✓ Deleted existing patients")

        inserted_count = 0
        async with pool.acquire() as conn:
            for patient_data in SAMPLE_PATIENTS:
                patient_id = str(uuid.uuid4())

                # Calculate age
                dob = date.fromisoformat(patient_data["date_of_birth"])
                today = date.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

                await conn.execute("""
                    INSERT INTO patients (
                        patient_id, first_name, last_name, date_of_birth, age, gender,
                        email, phone, address, emergency_contact, blood_type,
                        allergies, chronic_conditions, insurance_info,
                        is_active, created_at, updated_at
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                """,
                    patient_id,
                    patient_data["first_name"],
                    patient_data["last_name"],
                    dob,
                    age,
                    patient_data["gender"],
                    patient_data["email"],
                    patient_data["phone"],
                    json.dumps(patient_data.get("address")),
                    json.dumps(patient_data.get("emergency_contact")),
                    patient_data.get("blood_type"),
                    json.dumps(patient_data.get("allergies", [])),
                    json.dumps(patient_data.get("chronic_conditions", [])),
                    json.dumps(patient_data.get("insurance_info")),
                    True
                )

                inserted_count += 1
                print(f"✓ Inserted: {patient_data['first_name']} {patient_data['last_name']} - Age {age}, {patient_data['gender']}")

        print(f"\n✓ Successfully seeded {inserted_count} patients")

        async with pool.acquire() as conn:
            total = await conn.fetchval("SELECT COUNT(*) FROM patients")
            print(f"✓ Total patients in database: {total}")

        await pool.close()
        print("✓ Database connection closed")

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(seed_patients())
