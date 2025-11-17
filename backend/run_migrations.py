"""
Script to run database migrations
Creates all tables defined in the SQL schema
"""
import asyncio
import asyncpg
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(".env")


async def run_migrations():
    """Run database migrations"""
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

        # Read SQL schema file
        sql_file_path = "database/postgresql/scripts/create_tables.sql"

        if not os.path.exists(sql_file_path):
            print(f"✗ SQL file not found: {sql_file_path}")
            return

        with open(sql_file_path, 'r') as f:
            sql_script = f.read()

        print(f"✓ Read SQL schema file: {sql_file_path}")

        # Execute SQL script
        print("Running migrations...")
        await conn.execute(sql_script)

        print("✓ Migrations completed successfully!")

        # Verify tables were created
        tables_query = """
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename;
        """

        tables = await conn.fetch(tables_query)

        print(f"\n✓ Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table['tablename']}")

        # Close connection
        await conn.close()
        print("\n✓ Database connection closed")

    except Exception as e:
        print(f"\n✗ Error running migrations: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(run_migrations())
