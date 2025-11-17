# Run Locally - Complete Guide

## Prerequisites

✅ Python 3.10 or higher
✅ Google Cloud account
✅ gcloud CLI installed

## Step-by-Step Setup

### 1. Install uv Package Manager

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart your terminal, then verify
uv --version
```

### 2. Setup Project

```bash
# Navigate to backend
cd backend

# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate    # Windows
```

### 3. Install Dependencies

```bash
# Install all dependencies
uv pip install -e .

# This installs:
# - FastAPI
# - Uvicorn
# - Google Cloud BigQuery
# - Pydantic
# - and all other dependencies
```

### 4. Setup Google Cloud Authentication

**Choose ONE method:**

#### Method A: Application Default Credentials (Recommended)

```bash
gcloud auth application-default login
```

This opens your browser to sign in. This is the easiest method!

#### Method B: Service Account Key

1. Go to [GCP Console](https://console.cloud.google.com)
2. Navigate to **IAM & Admin** → **Service Accounts**
3. Create or select a service account
4. Add role: **BigQuery Admin**
5. Go to **Keys** tab → **Add Key** → **Create New Key** → **JSON**
6. Download the JSON file
7. Save it securely (e.g., `~/gcp-keys/careagents-sa.json`)

### 5. Configure Environment Variables

The `.env` file is already created. **Edit it with your values:**

```bash
# Open in your editor
nano .env
# or
code .env
# or
vim .env
```

**Update these values:**

```env
# REQUIRED: Your GCP Project ID
GCP_PROJECT_ID=my-healthcare-project

# OPTIONAL: Only needed if using Method B above
GCP_CREDENTIALS_PATH=/Users/yourname/gcp-keys/careagents-sa.json

# These can stay as-is
BIGQUERY_DATASET_ID=healthcare_db
GCP_LOCATION=US
ENVIRONMENT=development
```

**To find your Project ID:**
```bash
gcloud projects list
```

### 6. Create BigQuery Database

```bash
# Make sure .venv is activated and you're in backend/

# Create dataset
python database/bigquery/scripts/create_dataset.py

# Create tables
python database/bigquery/scripts/create_tables.py
```

**Expected output:**
```
Creating BigQuery dataset...
Project ID: my-healthcare-project
Dataset ID: healthcare_db
Location: US
--------------------------------------------------
✓ Created dataset my-healthcare-project.healthcare_db
  Location: US
  Description: Healthcare database for patient records...

✓ Dataset creation completed successfully
```

```
Creating BigQuery tables...
Project: my-healthcare-project
Dataset: healthcare_db
------------------------------------------------------------

patients:
  ✓ Created table patients
    Columns: 16

doctors:
  ✓ Created table doctors
    Columns: 18

...

============================================================
Tables created: 6/6
✓ All tables created successfully!
```

### 7. Start the Server

```bash
# Method 1: Using make (recommended)
make run

# Method 2: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Method 3: Using python
python main.py
```

**You should see:**
```
Starting Healthcare Management System...
Project ID: my-healthcare-project
Dataset: healthcare_db
✓ Connected to BigQuery: my-healthcare-project.healthcare_db
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 8. Test the API

#### Browser (Easiest Way)

Open in your browser:

- 🔥 **Interactive API Docs**: http://localhost:8000/docs
- 📚 **Alternative Docs**: http://localhost:8000/redoc
- ❤️ **Health Check**: http://localhost:8000/health

#### Using the Interactive Docs

1. Go to http://localhost:8000/docs
2. You'll see all available endpoints
3. Click on **POST /api/v1/patients/**
4. Click **"Try it out"** button
5. You'll see a JSON example - modify it or use as-is:

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-15",
  "gender": "Male",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "blood_type": "A+"
}
```

6. Click **"Execute"**
7. Scroll down to see the response!

#### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Create a patient
curl -X POST "http://localhost:8000/api/v1/patients/" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith",
    "date_of_birth": "1985-05-20",
    "gender": "Female",
    "email": "jane@example.com",
    "blood_type": "O+"
  }'

# List patients
curl "http://localhost:8000/api/v1/patients/?page=1&page_size=10"

# Get specific patient (use patient_id from create response)
curl "http://localhost:8000/api/v1/patients/PATIENT_ID_HERE"

# Search patients
curl "http://localhost:8000/api/v1/patients/search/?q=jane"
```

### 9. Verify Data in BigQuery

```bash
# List all patients
bq query --use_legacy_sql=false \
  'SELECT * FROM `my-healthcare-project.healthcare_db.patients` LIMIT 10'

# Or open BigQuery Console
gcloud console sql
```

## Available Make Commands

```bash
make help          # Show all commands
make install       # Install dependencies
make run           # Start development server
make clean         # Clean cache files
make setup-db      # Create dataset and tables
make format        # Format code with black
make lint          # Lint code with ruff
```

## Common Issues & Solutions

### ❌ "Module not found: database"

**Solution:**
```bash
cd backend
source .venv/bin/activate
uv pip install -e .
```

### ❌ "Failed to connect to BigQuery"

**Solution 1** - Check authentication:
```bash
gcloud auth application-default login
```

**Solution 2** - Verify project ID:
```bash
# Check your current project
gcloud config get-value project

# List all projects
gcloud projects list

# Update .env with correct project ID
```

**Solution 3** - Check service account key (if using Method B):
```bash
# Verify file exists
ls -la /path/to/your-key.json

# Verify path in .env matches
cat .env | grep GCP_CREDENTIALS_PATH
```

### ❌ "Dataset not found"

**Solution:**
```bash
python database/bigquery/scripts/create_dataset.py
```

### ❌ "Table not found"

**Solution:**
```bash
python database/bigquery/scripts/create_tables.py
```

### ❌ "Permission denied" when accessing BigQuery

**Solution:**
```bash
# Grant yourself BigQuery Admin role
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="user:YOUR_EMAIL@gmail.com" \
    --role="roles/bigquery.admin"
```

### ❌ "Port 8000 already in use"

**Solution 1** - Use different port:
```bash
uvicorn main:app --reload --port 8001
```

**Solution 2** - Kill process:
```bash
# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### ❌ "uv: command not found"

**Solution:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart terminal
source ~/.bashrc  # or ~/.zshrc

# Verify
uv --version
```

## Project Structure

```
backend/
├── .env                      # Your configuration (EDIT THIS!)
├── .venv/                    # Virtual environment (created by uv)
├── database/bigquery/
│   ├── schemas/              # Table definitions
│   ├── scripts/              # Setup scripts
│   ├── connection.py         # DB connection
│   └── repository.py         # CRUD operations
├── models/                   # Pydantic models
├── routes/                   # API endpoints
├── services/                 # Business logic
├── main.py                   # App entry point
├── pyproject.toml            # Dependencies
└── Makefile                  # Helper commands
```

## Development Workflow

1. **Make changes** to code
2. **Server auto-reloads** (if using `--reload`)
3. **Test** at http://localhost:8000/docs
4. **Check logs** in terminal
5. **Query BigQuery** to verify data

## Next Steps

✅ Server is running
✅ Create some patients via /docs
✅ Test the search functionality
✅ View data in BigQuery Console
✅ Explore the code structure
✅ Implement doctors endpoints (follow patient pattern)

## Resources

- **API Docs**: http://localhost:8000/docs
- **Project Summary**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)

## Need Help?

1. Check this guide again
2. Review error messages carefully
3. Check GCP Console for permissions
4. Verify .env configuration
5. Check terminal logs

**Happy coding! 🎉**


.PHONY: help install dev run test format lint clean setup-db docker-build docker-run deploy

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies using uv"
	@echo "  make dev          - Install dev dependencies"
	@echo "  make run          - Run the application locally"
	@echo "  make test         - Run tests"
	@echo "  make format       - Format code with black"
	@echo "  make lint         - Lint code with ruff"
	@echo "  make clean        - Clean up cache and build files"
	@echo "  make setup-db     - Create BigQuery dataset and tables"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run Docker container locally"
	@echo "  make deploy       - Deploy to Cloud Run"

install:
	@echo "Installing dependencies with uv..."
	uv venv
	uv pip install -e .
	@echo "✓ Dependencies installed"

dev:
	@echo "Installing dev dependencies..."
	uv pip install -e ".[dev]"
	@echo "✓ Dev dependencies installed"

run:
	@echo "Starting development server..."
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

test:
	@echo "Running tests..."
	pytest

format:
	@echo "Formatting code..."
	black .
	@echo "✓ Code formatted"

lint:
	@echo "Linting code..."
	ruff check .

clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleaned"

setup-db:
	@echo "Setting up BigQuery database..."
	python database/bigquery/scripts/create_dataset.py
	python database/bigquery/scripts/create_tables.py
	@echo "✓ Database setup complete"

docker-build:
	@echo "Building Docker image..."
	docker build -t careagents-backend .
	@echo "✓ Docker image built"

docker-run:
	@echo "Running Docker container..."
	docker run -p 8080:8080 \
		-e GCP_PROJECT_ID=${GCP_PROJECT_ID} \
		-e BIGQUERY_DATASET_ID=healthcare_db \
		-e GCP_LOCATION=US \
		-e GCP_CREDENTIALS_PATH=/tmp/keys/key.json \
		-v $(HOME)/.config/gcloud/application_default_credentials.json:/tmp/keys/key.json:ro \
		careagents-backend

deploy:
	@echo "Deploying to Cloud Run..."
	@if [ -z "$(GCP_PROJECT_ID)" ]; then \
		echo "Error: GCP_PROJECT_ID not set"; \
		echo "Usage: GCP_PROJECT_ID=your-project make deploy"; \
		exit 1; \
	fi
	gcloud run deploy careagents-backend \
		--source . \
		--region us-central1 \
		--allow-unauthenticated \
		--set-env-vars "GCP_PROJECT_ID=${GCP_PROJECT_ID},BIGQUERY_DATASET_ID=healthcare_db,GCP_LOCATION=US" \
		--memory 512Mi \
		--cpu 1 \
		--min-instances 0 \
		--max-instances 10 \
		--port 8080
	@echo "✓ Deployed to Cloud Run"
