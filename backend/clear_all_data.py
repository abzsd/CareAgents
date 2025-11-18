"""
Script to delete all data from all tables
"""
import asyncio
import asyncpg
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(".env")


async def clear_all_data():
    """Clear all data from all tables"""
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

        # Disable foreign key checks temporarily
        await conn.execute("SET session_replication_role = 'replica';")

        # Get all tables
        tables_query = """
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename;
        """

        tables = await conn.fetch(tables_query)

        print(f"\n🗑️  Clearing data from {len(tables)} tables...")

        for table in tables:
            table_name = table['tablename']
            try:
                await conn.execute(f"TRUNCATE TABLE {table_name} CASCADE;")
                print(f"  ✓ Cleared {table_name}")
            except Exception as e:
                print(f"  ✗ Error clearing {table_name}: {str(e)}")

        # Re-enable foreign key checks
        await conn.execute("SET session_replication_role = 'origin';")

        print("\n✓ All data cleared successfully!")

        # Close connection
        await conn.close()
        print("✓ Database connection closed")

    except Exception as e:
        print(f"\n✗ Error clearing data: {str(e)}")
        raise


if __name__ == "__main__":
    print("⚠️  WARNING: This will delete ALL data from the database!")
    confirm = input("Are you sure you want to continue? (yes/no): ")

    if confirm.lower() == 'yes':
        asyncio.run(clear_all_data())
    else:
        print("Operation cancelled")
