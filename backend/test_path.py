import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

print("Current working directory:", os.getcwd())
print("__file__:", __file__)
print("File directory:", os.path.dirname(__file__))
print("Parent directory:", os.path.dirname(os.path.dirname(__file__)))
print("Grand parent directory:", os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Test path resolution
test_path = Path("../../.env")
print(f"Test path: {test_path}")
print(f"Absolute path: {test_path.absolute()}")
print(f"File exists: {test_path.exists()}")

# Load environment variables
from dotenv import load_dotenv
load_dotenv(test_path)

print("=== After dotenv load ===")
print(f"GCP_PROJECT_ID: {os.getenv('GCP_PROJECT_ID')}")
print(f"BIGQUERY_DATASET_ID: {os.getenv('BIGQUERY_DATASET_ID')}")
print(f"GCP_LOCATION: {os.getenv('GCP_LOCATION')}")
