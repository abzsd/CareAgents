# Healthcare Management Backend

A FastAPI-based backend system for healthcare data management using Google BigQuery as the database.

## Features

- **Patient Management**: Complete CRUD operations for patient records
- **Doctor Management**: Doctor profiles with organization affiliations
- **Health Vitals**: Track patient vitals including blood pressure, heart rate, diabetes status, etc.
- **Prescriptions**: Manage prescriptions with medication details
- **Medical Reports**: Store and manage lab tests, radiology reports, and other medical documents
- **Organizations**: Healthcare organizations (hospitals, clinics) management

## Tech Stack

- **Framework**: FastAPI
- **Database**: Google BigQuery
- **Validation**: Pydantic v2
- **Authentication**: (To be implemented)
- **Cloud Platform**: Google Cloud Platform

## Project Structure

```
backend/
├── database/
│   └── bigquery/
│       ├── schemas/           # BigQuery table schemas (JSON)
│       ├── scripts/           # Database setup scripts
│       ├── config.py          # Database configuration
│       ├── connection.py      # Connection manager
│       └── repository.py      # Base repository pattern
├── models/                    # Pydantic models
│   ├── patient.py
│   ├── doctor.py
│   └── health_vitals.py
├── routes/                    # API routes
│   └── patients.py
├── services/                  # Business logic layer
│   └── patient_service.py
├── main.py                    # FastAPI application
├── requirements.txt           # Python dependencies
└── README.md
```

## Setup Instructions

### Prerequisites

1. Python 3.10 or higher
2. Google Cloud Platform account
3. BigQuery API enabled
4. Service account with BigQuery permissions

### 1. Install uv Package Manager

```bash
# Install uv (fastest Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv
```

### 2. Clone and Install Dependencies

```bash
cd backend

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install project dependencies
uv pip install -e .
```

### 2. Configure Environment Variables

Copy the example environment file and update it:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
GCP_PROJECT_ID=your-gcp-project-id
GCP_LOCATION=US
GCP_CREDENTIALS_PATH=/path/to/service-account-key.json
BIGQUERY_DATASET_ID=healthcare_db
```

### 3. Set Up Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a service account
3. Grant BigQuery Admin role
4. Download the JSON key file
5. Update `GCP_CREDENTIALS_PATH` in `.env`

### 4. Create BigQuery Dataset and Tables

```bash
# Create the dataset
python database/bigquery/scripts/create_dataset.py

# Create all tables
python database/bigquery/scripts/create_tables.py
```

### 5. Run the Application

```bash
# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Patients

- `POST /api/v1/patients/` - Create a new patient
- `GET /api/v1/patients/{patient_id}` - Get patient by ID
- `GET /api/v1/patients/` - List patients (with pagination)
- `PUT /api/v1/patients/{patient_id}` - Update patient
- `DELETE /api/v1/patients/{patient_id}` - Soft delete patient
- `GET /api/v1/patients/search/?q=term` - Search patients

### Health Check

- `GET /health` - Check API and database health

## Database Schema

### Tables

1. **patients** - Patient demographic and contact information
2. **doctors** - Doctor profiles and credentials
3. **organizations** - Healthcare organizations
4. **prescriptions** - Medical prescriptions
5. **health_vitals** - Patient vital signs
6. **medical_reports** - Medical reports and lab results

## Example Usage

### Create a Patient

```bash
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

### Get Patient

```bash
curl "http://localhost:8000/api/v1/patients/{patient_id}"
```

### List Patients

```bash
curl "http://localhost:8000/api/v1/patients/?page=1&page_size=20"
```

## Development

### Adding New Endpoints

1. Create Pydantic models in `models/`
2. Create repository methods in `services/`
3. Create route handlers in `routes/`
4. Register router in `main.py`

### Repository Pattern

The base repository (`BaseRepository`) provides common CRUD operations:

```python
from database.bigquery.repository import BaseRepository

class CustomRepository(BaseRepository):
    def __init__(self, client, dataset_id, project_id):
        super().__init__(client, "table_name", dataset_id, project_id)

    # Add custom methods
    def custom_query(self):
        query = "SELECT * FROM ..."
        return self._execute_query(query)
```

## BigQuery Best Practices

1. **Use Partitioning**: For tables with time-series data
2. **Clustering**: Cluster tables by commonly filtered columns
3. **Avoid SELECT ***: Select only needed columns
4. **Use Query Parameters**: Prevent SQL injection
5. **Batch Inserts**: Use `insert_many()` for multiple records

## Security Considerations

1. Never commit `.env` file or service account keys
2. Use environment variables for sensitive data
3. Implement authentication and authorization
4. Validate all input data using Pydantic
5. Use HTTPS in production
6. Implement rate limiting
7. Sanitize error messages in production

## Production Deployment

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Configuration

- Set `ENVIRONMENT=production`
- Use proper CORS origins
- Enable authentication
- Configure logging
- Set up monitoring

## Next Steps

- [ ] Implement authentication and authorization
- [ ] Add endpoints for doctors, prescriptions, etc.
- [ ] Implement file upload for medical reports
- [ ] Add real-time notifications
- [ ] Implement audit logging
- [ ] Add data analytics endpoints
- [ ] Set up automated backups
- [ ] Implement caching layer
- [ ] Add comprehensive testing
- [ ] Set up CI/CD pipeline

## License

[Your License Here]

## Support

For issues and questions, please contact [your-email@example.com]
