"""
Fix missing doctor record for user who is marked as onboarded
"""
import asyncio
import asyncpg
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv(".env")


async def fix_missing_doctor():
    """Create doctor record for user marked as onboarded but missing doctor profile"""

    # Connect to PostgreSQL
    conn = await asyncpg.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 5432)),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres'),
        database=os.getenv('DB_NAME', 'healthcare_db')
    )

    try:
        # Find all users with role 'doctor' who are onboarded but don't have a doctor record
        query = """
            SELECT u.user_id, u.email, u.display_name
            FROM users u
            LEFT JOIN doctors d ON u.user_id = d.user_id
            WHERE u.role = 'doctor'
              AND u.is_onboarded = true
              AND d.doctor_id IS NULL
        """

        missing_doctors = await conn.fetch(query)

        if not missing_doctors:
            print("✓ No missing doctor records found")
            return

        print(f"Found {len(missing_doctors)} user(s) without doctor records:")

        for user in missing_doctors:
            user_id = user['user_id']
            email = user['email']
            display_name = user['display_name'] or "Doctor"

            # Split display name into first and last name
            name_parts = display_name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""

            print(f"\nCreating doctor record for: {display_name} ({email})")

            # Create doctor record
            insert_query = """
                INSERT INTO doctors (
                    doctor_id, user_id, first_name, last_name,
                    specialization, license_number, email,
                    is_active, created_at, updated_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING doctor_id
            """

            doctor_id = await conn.fetchval(
                insert_query,
                user_id,  # Use same ID for doctor_id
                user_id,
                first_name,
                last_name,
                'General Practice',  # Default specialization
                f'MD{str(uuid.uuid4())[:6].upper()}',  # Generate license number
                email,
                True,
                datetime.utcnow(),
                datetime.utcnow()
            )

            print(f"✓ Created doctor record: {doctor_id}")

        print(f"\n✓ Successfully created {len(missing_doctors)} doctor record(s)")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(fix_missing_doctor())
