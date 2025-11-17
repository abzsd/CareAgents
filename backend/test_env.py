import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(".env")
print(f"Looking for .env file at: {env_path.absolute()}")
print(f"File exists: {env_path.exists()}")

load_dotenv(env_path)

# Print environment variables
print(f"GCP_PROJECT_ID: {os.getenv('GCP_PROJECT_ID', 'Not found')}")
print(f"BIGQUERY_DATASET_ID: {os.getenv('BIGQUERY_DATASET_ID', 'Not found')}")
print(f"GCP_LOCATION: {os.getenv('GCP_LOCATION', 'Not found')}")
