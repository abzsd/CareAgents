# CareAgents - Medical History Management Setup

This guide will help you set up the medical history management system with all its features.

## Features Implemented

### Backend
- ✅ Medical history database schema with PostgreSQL
- ✅ Medical history CRUD endpoints
- ✅ Patient management endpoints
- ✅ File upload service with Google Cloud Storage
- ✅ Doctor-patient relationship tracking

### Frontend
- ✅ **Patient Dashboard**: View medical history with detailed records
- ✅ **Doctor Dashboard**: View all patients and their medical history
- ✅ **Patient Detail View**: Complete patient information with medical history
- ✅ **Medical Record Form**: Create prescriptions with file uploads
- ✅ Responsive UI with proper navigation and state management

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Edit `backend/.env` and configure your database:

```env
# For local PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=healthcare_db
DB_USER=postgres
DB_PASSWORD=postgres

# Google Cloud Storage (optional for file uploads)
GCS_BUCKET_NAME=healthcare-prescriptions
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

### 3. Create Database

```bash
# Create the database (if not exists)
psql -U postgres -c "CREATE DATABASE healthcare_db;"
```

### 4. Run Database Migrations

```bash
cd backend
python run_migrations.py
```

This will create all necessary tables:
- `users`
- `patients`
- `doctors`
- `prescriptions`
- `health_vitals`
- `medical_reports`
- `medical_history` (new)
- `organizations`

### 5. Start Backend Server

```bash
cd backend
python main.py
# Or use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 3. Start Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at: http://localhost:5173

## API Endpoints

### Medical History Endpoints

- `POST /api/v1/medical-history/` - Create medical history record
- `GET /api/v1/medical-history/{history_id}` - Get specific record
- `GET /api/v1/medical-history/patient/{patient_id}` - Get patient's history
- `GET /api/v1/medical-history/doctor/{doctor_id}/patients` - Get doctor's patients
- `GET /api/v1/medical-history/patients/all` - Get all patients
- `PUT /api/v1/medical-history/{history_id}` - Update record
- `DELETE /api/v1/medical-history/{history_id}` - Delete record

### File Upload Endpoints

- `POST /api/v1/files/upload` - Upload prescription/report files
- `DELETE /api/v1/files/delete/{blob_name}` - Delete uploaded file
- `GET /api/v1/files/list` - List uploaded files

## Usage Guide

### For Patients

1. **Login** with patient credentials
2. **View Overview**: See quick stats and health summary
3. **Medical History Tab**:
   - View all past medical records
   - Click on any record to see detailed information
   - View prescriptions, symptoms, diagnosis, etc.

### For Doctors

1. **Login** with doctor credentials
2. **Dashboard Tab**: Quick actions and statistics
3. **Patients Tab**:
   - **All Patients**: View all patients in the system
   - **My Patients**: View patients you've treated
   - **Search**: Find patients by name, email, or phone
4. **Patient Details**:
   - Click on any patient to view complete details
   - See patient's medical history
   - View allergies, chronic conditions, contact info
5. **Add Medical Record**:
   - Click "Add Medical Record" button
   - Fill in visit date, diagnosis, symptoms
   - Add prescriptions with dosage and instructions
   - Upload prescription files (images, PDFs)
   - Add blood pressure and health status
   - Set follow-up dates

## Google Cloud Storage Setup (Optional)

For file uploads to work, you need to configure Google Cloud Storage:

1. **Create a GCS Bucket**:
   ```bash
   gsutil mb gs://healthcare-prescriptions
   ```

2. **Create Service Account**:
   - Go to Google Cloud Console
   - Create a service account
   - Grant "Storage Object Creator" and "Storage Object Viewer" roles
   - Download JSON key file

3. **Set Environment Variable**:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
   ```

4. **Update .env**:
   ```env
   GCS_BUCKET_NAME=healthcare-prescriptions
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   ```

## Database Schema

### medical_history Table

```sql
CREATE TABLE medical_history (
    history_id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) REFERENCES patients(patient_id),
    doctor_id VARCHAR(36) REFERENCES doctors(doctor_id),
    doctor_name VARCHAR(255) NOT NULL,
    visit_date DATE NOT NULL,
    diagnosis TEXT,
    prescriptions JSONB,
    health_status VARCHAR(100),
    blood_pressure VARCHAR(20),
    symptoms JSONB,
    notes TEXT,
    follow_up_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Testing the API

You can test the API using the interactive docs at http://localhost:8000/docs

Example: Create a medical history record

```bash
curl -X POST "http://localhost:8000/api/v1/medical-history/" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient-uuid",
    "doctor_name": "Dr. John Smith",
    "visit_date": "2025-11-18",
    "diagnosis": "Common cold with mild fever",
    "prescriptions": [
      {
        "medication_name": "Paracetamol",
        "dosage": "500mg",
        "frequency": "3 times a day",
        "duration": "5 days",
        "instructions": "Take after meals"
      }
    ],
    "health_status": "Stable",
    "blood_pressure": "120/80",
    "symptoms": ["fever", "headache", "fatigue"],
    "notes": "Rest recommended for 3 days"
  }'
```

## Troubleshooting

### Database Connection Issues

- Check PostgreSQL is running: `pg_isready`
- Verify credentials in `.env`
- Ensure database exists: `psql -U postgres -l`

### Frontend API Connection Issues

- Check `VITE_API_BASE_URL` in frontend `.env`
- Ensure backend is running on port 8000
- Check browser console for CORS errors

### File Upload Issues

- Verify GCS credentials are set
- Check bucket exists and has proper permissions
- Review backend logs for detailed error messages

## Next Steps

- **AI Integration**: The system is ready for integration with Google's Agentic Development Kit (ADK) for AI-powered medical assistance
- **Appointments**: Extend the system to handle appointment scheduling
- **Telemedicine**: Add video consultation features
- **Analytics**: Add health analytics and reporting features

## Support

For issues or questions, please check:
- Backend API docs: http://localhost:8000/docs
- Database logs: Check PostgreSQL logs
- Application logs: Check terminal output where servers are running
