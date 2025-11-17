"""
FastAPI Main Application
Healthcare Management System with PostgreSQL Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from routes import patients, users, chat, medical_history, files
from database.postgresql.connection import get_postgresql_connection
import dotenv
dotenv.load_dotenv(".env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Initialize resources on startup, cleanup on shutdown.
    """
    # Startup
    print("Starting Healthcare Management System with PostgreSQL...")
    print(f"Database Host: {os.getenv('DB_HOST', 'localhost')}")
    print(f"Database Name: {os.getenv('DB_NAME', 'healthcare_db')}")

    # Verify PostgreSQL connection
    try:
        connection = get_postgresql_connection()
        pool = await connection.get_pool()
        print(f"✓ Connected to PostgreSQL: {connection.host}:{connection.port}/{connection.database}")
        
        # Test connection with a simple query
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1 as health_check")
            if result == 1:
                print("✓ PostgreSQL connection test successful")
    except Exception as e:
        print(f"✗ Failed to connect to PostgreSQL: {str(e)}")

    yield

    # Shutdown
    print("Shutting down Healthcare Management System...")
    try:
        connection = get_postgresql_connection()
        await connection.close()
        print("✓ PostgreSQL connection closed")
    except Exception as e:
        print(f"Error during shutdown: {str(e)}")


# Initialize FastAPI app
app = FastAPI(
    title="Healthcare Management API",
    description="RESTful API for healthcare data management using PostgreSQL",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(patients.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(medical_history.router, prefix="/api/v1")
app.include_router(files.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Healthcare Management API",
        "version": "1.0.0",
        "database": "PostgreSQL",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Verifies PostgreSQL connection.
    """
    try:
        connection = get_postgresql_connection()
        pool = await connection.get_pool()

        # Test connection with a simple query
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1 as health_check")

        return {
            "status": "healthy",
            "database": "connected",
            "database_type": "PostgreSQL",
            "host": connection.host,
            "database": connection.database
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "database_type": "PostgreSQL",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn

    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
