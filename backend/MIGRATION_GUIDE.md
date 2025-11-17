# BigQuery to PostgreSQL Migration Guide

This guide explains how to migrate from BigQuery to PostgreSQL while keeping the same business logic and API endpoints.

## Overview

The migration maintains the same:
- API endpoints and request/response formats
- Business logic in services
- Data models and validation
- Repository pattern for data access

## What Changed

### Database Layer
- **Before**: BigQuery with batch loading and streaming inserts
- **After**: PostgreSQL with connection pooling and async operations

### Dependencies
- **Added**: `asyncpg==0.29.0` for PostgreSQL async driver
- **Kept**: BigQuery dependencies for backward compatibility during migration

### File Structure
```
backend/
├── database/
│   ├── bigquery/          # Original BigQuery implementation
│   └── postgresql/        # New PostgreSQL implementation
│       ├── config.py      # Database configuration
│       ├── connection.py  # Connection pooling
│       ├── repository.py  # Base repository pattern
│       └── scripts/
│           └── create_tables.sql  # Database schema
├── services/
│   ├── user_service.py           # Original BigQuery service
│   ├── user_service_postgresql.py    # New PostgreSQL service
│   ├── patient_service.py        # Original BigQuery service
│   └── patient_service_postgresql.py # New PostgreSQL service
├── routes/
│   ├── users.py              # Original BigQuery routes
│   ├── users_postgresql.py   # New PostgreSQL routes
│   ├── patients.py           # Original BigQuery routes
│   └── patients_postgresql.py # New PostgreSQL routes
├── main.py                   # Original BigQuery app
└── main_postgresql.py       # New PostgreSQL app
```

## Migration Steps

### 1. Set Up PostgreSQL Database

Install PostgreSQL and create the database:
```bash
# Install PostgreSQL (macOS)
brew install postgresql
brew services start postgresql

# Create database
createdb healthcare_db

# Run schema creation
psql healthcare_db < backend/database/postgresql/scripts/create_tables.sql
```

### 2. Configure Environment

Copy the PostgreSQL environment template:
```bash
cp backend/.env.postgresql.example backend/.env
```

Update the `.env` file with your PostgreSQL credentials:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=healthcare_db
DB_USER=postgres
DB_PASSWORD=your_password
```

### 3. Install Dependencies

Install the new PostgreSQL dependency:
```bash
cd backend
pip install asyncpg==0.29.0
```

### 4. Run the PostgreSQL Application

Start the new PostgreSQL-based application:
```bash
cd backend
python main_postgresql.py
```

The application will be available at `http://localhost:8000`

### 5. Test the Migration

Test the health endpoint:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "database_type": "PostgreSQL",
  "host": "localhost",
  "database": "healthcare_db"
}
```

## Key Differences

### Connection Management
- **BigQuery**: Singleton client with service account authentication
- **PostgreSQL**: Connection pooling with configurable min/max connections

### Data Operations
- **BigQuery**: Batch loading with temporary files for inserts
- **PostgreSQL**: Direct async insert/update operations

### Query Syntax
- **BigQuery**: Standard SQL with `@parameter` placeholders
- **PostgreSQL**: PostgreSQL SQL with `$1, $2, ...` placeholders

### JSON Handling
- **BigQuery**: Native JSON support with automatic conversion
- **PostgreSQL**: JSONB columns with explicit JSON serialization

## API Compatibility

All API endpoints remain the same:
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{user_id}` - Get user by ID
- `GET /api/v1/users/firebase/{firebase_uid}` - Get user by Firebase UID
- `PUT /api/v1/users/{user_id}` - Update user
- `POST /api/v1/patients/` - Create patient
- `GET /api/v1/patients/{patient_id}` - Get patient
- `GET /api/v1/patients/` - List patients with pagination
- `PUT /api/v1/patients/{patient_id}` - Update patient
- `DELETE /api/v1/patients/{patient_id}` - Soft delete patient
- `GET /api/v1/patients/search/` - Search patients

## Performance Improvements

### Connection Pooling
PostgreSQL uses connection pooling which provides:
- Better resource utilization
- Reduced connection overhead
- Configurable pool size

### Indexing
The PostgreSQL schema includes optimized indexes:
- Primary key indexes on all ID fields
- Unique indexes on email and Firebase UID
- Foreign key indexes for relationships
- Search indexes for common query patterns

### Triggers
Automatic `updated_at` timestamp updates using PostgreSQL triggers.

## Rollback Plan

To rollback to BigQuery:
1. Stop the PostgreSQL application
2. Start the original BigQuery application: `python main.py`
3. Update environment variables to use BigQuery configuration

## Data Migration

To migrate existing data from BigQuery to PostgreSQL:

1. Export data from BigQuery:
```sql
EXPORT DATA OPTIONS(
  uri='gs://your-bucket/users/*.json',
  format='JSON'
) AS
SELECT * FROM `project.dataset.users`;
```

2. Import to PostgreSQL using the provided scripts or custom migration tools.

## Monitoring and Logging

The PostgreSQL implementation includes:
- Connection pool monitoring
- Query performance logging
- Error handling and reporting
- Health check endpoints

## Security Considerations

- Use connection pooling with proper authentication
- Enable SSL for production deployments
- Implement proper database user permissions
- Use environment variables for sensitive configuration

## Production Deployment

For production deployment:
1. Use a managed PostgreSQL service (AWS RDS, Google Cloud SQL, etc.)
2. Configure SSL connections
3. Set up proper backup and recovery procedures
4. Monitor connection pool metrics
5. Implement proper logging and alerting
