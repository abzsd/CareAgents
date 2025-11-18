"""
Script to add user_id to patients table
"""
import asyncio
import asyncpg
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(".env")


async def run_migration():
    """Run migration to add user_id to patients table"""
    # Database connection parameters
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "5432"))
    database = os.getenv("DB_NAME", "healthcare_db")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")

    print(f"Connecting to database: {host}:{port}/{database}")

    try:
        # Connect to database
        conn = await asyncpg.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )

        print("✓ Connected to database")

        # Read SQL migration file
        sql_file_path = "database/postgresql/scripts/add_user_id_to_patients.sql"

        if not os.path.exists(sql_file_path):
            print(f"✗ SQL file not found: {sql_file_path}")
            return

        with open(sql_file_path, 'r') as f:
            sql_script = f.read()

        print(f"✓ Read migration file: {sql_file_path}")

        # Execute SQL script
        print("Running migration...")
        await conn.execute(sql_script)

        print("✓ Migration completed successfully!")

        # Close connection
        await conn.close()
        print("✓ Database connection closed")

    except Exception as e:
        print(f"\n✗ Error running migration: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(run_migration())
