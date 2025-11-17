# Start Locally - Quick Guide

Follow these steps to run the backend locally right now.

## Step 1: Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv
```

## Step 2: Install Dependencies

```bash
cd backend

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the project
uv pip install -e .
```

## Step 3: Setup Google Cloud Credentials

### Option A: Use Application Default Credentials (Easiest)

```bash
gcloud auth application-default login
```

This will open a browser window. Sign in with your Google account that has access to your GCP project.

### Option B: Use Service Account Key

1. Download your service account JSON key from GCP Console
2. Save it somewhere safe (e.g., `~/gcp-keys/careagents-key.json`)

## Step 4: Create `.env` File

```bash
# Copy the example
cp .env.example .env
```

Edit the `.env` file with your values:

```env
# Your GCP Project ID (REQUIRED)
GCP_PROJECT_ID=your-actual-project-id

# If using service account key (Option B above)
GCP_CREDENTIALS_PATH=/path/to/your/service-account-key.json

# BigQuery settings
BIGQUERY_DATASET_ID=healthcare_db
GCP_LOCATION=US

# Local development settings
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
```

## Step 5: Create BigQuery Dataset and Tables

```bash
# Make sure you're in the backend directory with venv activated

# Create the dataset
python database/bigquery/scripts/create_dataset.py

# Create all tables
python database/bigquery/scripts/create_tables.py
```

You should see:
```
✓ Created dataset your-project-id.healthcare_db
...
✓ All tables created successfully!
```

## Step 6: Run the Application

```bash
# Using make (recommended)
make run

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using python
python main.py
```

You should see:
```
Starting Healthcare Management System...
Project ID: your-project-id
Dataset: healthcare_db
✓ Connected to BigQuery: your-project-id.healthcare_db
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 7: Test the API

### Open in Browser

- **API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Test with cURL

```bash
# Health check
curl http://localhost:8000/health

# Should return:
# {
#   "status": "healthy",
#   "database": "connected",
#   "project": "your-project-id",
#   "dataset": "healthcare_db"
# }

# Create a patient
curl -X POST "http://localhost:8000/api/v1/patients/" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-15",
    "gender": "Male",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "blood_type": "A+"
  }'
```

### Use the Interactive Docs (Easiest!)

1. Go to http://localhost:8000/docs
2. Click on **POST /api/v1/patients/**
3. Click **Try it out**
4. Fill in the example data
5. Click **Execute**
6. See the response!

## Troubleshooting

### Issue: "Module not found"

```bash
# Make sure you're in the backend directory
cd backend

# Activate virtual environment
source .venv/bin/activate

# Reinstall
uv pip install -e .
```

### Issue: "Failed to connect to BigQuery"

```bash
# Check if you're authenticated
gcloud auth application-default login

# Or verify your service account key path in .env
cat .env | grep GCP_CREDENTIALS_PATH
```

### Issue: "Dataset not found"

```bash
# Create the dataset
python database/bigquery/scripts/create_dataset.py
```

### Issue: "Table not found"

```bash
# Create the tables
python database/bigquery/scripts/create_tables.py
```

### Issue: "Port 8000 already in use"

```bash
# Use a different port
uvicorn main:app --reload --port 8001

# Or kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```

## Next Steps

Once running:

1. **Explore the API** at http://localhost:8000/docs
2. **Create some patients** using the UI
3. **Test the search** functionality
4. **View data in BigQuery Console**
5. **Check the logs** in your terminal

## Quick Commands Reference

```bash
# Start the server
make run

# Clean cache files
make clean

# Format code
make format

# Run tests (when implemented)
make test
```

## Need Help?

- Check [LOCAL_SETUP.md](LOCAL_SETUP.md) for detailed setup
- Review [README.md](README.md) for full documentation
- See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for overview

Happy coding! 🚀
