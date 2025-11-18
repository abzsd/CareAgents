-- PostgreSQL Database Schema for Healthcare Management System
-- Create tables for users, patients, doctors, organizations, prescriptions, health_vitals, and medical_reports

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    photo_url TEXT,
    role VARCHAR(50) NOT NULL DEFAULT 'patient',
    is_onboarded BOOLEAN DEFAULT FALSE,
    firebase_uid VARCHAR(255) UNIQUE NOT NULL,
    provider_id VARCHAR(255) NOT NULL,
    last_login_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Patients table
CREATE TABLE IF NOT EXISTS patients (
    patient_id VARCHAR(36) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    age INTEGER,
    gender VARCHAR(50) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    address JSONB,
    emergency_contact JSONB,
    blood_type VARCHAR(10),
    allergies JSONB,
    chronic_conditions JSONB,
    insurance_info JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Doctors table
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(user_id),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    specialization VARCHAR(255),
    license_number VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    email VARCHAR(255),
    address JSONB,
    experience_years INTEGER,
    education JSONB,
    certifications JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Organizations table
CREATE TABLE IF NOT EXISTS organizations (
    organization_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    address JSONB,
    phone VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),
    license_number VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prescriptions table
CREATE TABLE IF NOT EXISTS prescriptions (
    prescription_id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) REFERENCES patients(patient_id),
    doctor_id VARCHAR(36) REFERENCES doctors(doctor_id),
    medications JSONB NOT NULL,
    diagnosis TEXT,
    notes TEXT,
    prescribed_date DATE NOT NULL,
    valid_until DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Health vitals table
CREATE TABLE IF NOT EXISTS health_vitals (
    vital_id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) REFERENCES patients(patient_id),
    recorded_by VARCHAR(36) REFERENCES users(user_id),
    vital_type VARCHAR(100) NOT NULL,
    value DECIMAL(10,2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    recorded_at TIMESTAMP NOT NULL,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Medical reports table
CREATE TABLE IF NOT EXISTS medical_reports (
    report_id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) REFERENCES patients(patient_id),
    doctor_id VARCHAR(36) REFERENCES doctors(doctor_id),
    report_type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    file_url TEXT,
    report_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Medical history table
CREATE TABLE IF NOT EXISTS medical_history (
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

-- Appointments table
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) REFERENCES patients(patient_id),
    doctor_id VARCHAR(36) REFERENCES doctors(doctor_id),
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    appointment_type VARCHAR(50) NOT NULL DEFAULT 'consultation',
    status VARCHAR(50) NOT NULL DEFAULT 'scheduled',
    reason TEXT,
    notes TEXT,
    location VARCHAR(255),
    duration_minutes INTEGER DEFAULT 30,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_firebase_uid ON users(firebase_uid);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_patients_email ON patients(email);
CREATE INDEX IF NOT EXISTS idx_doctors_user_id ON doctors(user_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_patient_id ON prescriptions(patient_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_doctor_id ON prescriptions(doctor_id);
CREATE INDEX IF NOT EXISTS idx_health_vitals_patient_id ON health_vitals(patient_id);
CREATE INDEX IF NOT EXISTS idx_medical_reports_patient_id ON medical_reports(patient_id);
CREATE INDEX IF NOT EXISTS idx_medical_reports_doctor_id ON medical_reports(doctor_id);
CREATE INDEX IF NOT EXISTS idx_medical_history_patient_id ON medical_history(patient_id);
CREATE INDEX IF NOT EXISTS idx_medical_history_doctor_id ON medical_history(doctor_id);
CREATE INDEX IF NOT EXISTS idx_appointments_patient_id ON appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor_id ON appointments(doctor_id);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at (drop if exists first)
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
DROP TRIGGER IF EXISTS update_patients_updated_at ON patients;
DROP TRIGGER IF EXISTS update_doctors_updated_at ON doctors;
DROP TRIGGER IF EXISTS update_organizations_updated_at ON organizations;
DROP TRIGGER IF EXISTS update_prescriptions_updated_at ON prescriptions;
DROP TRIGGER IF EXISTS update_health_vitals_updated_at ON health_vitals;
DROP TRIGGER IF EXISTS update_medical_reports_updated_at ON medical_reports;
DROP TRIGGER IF EXISTS update_medical_history_updated_at ON medical_history;
DROP TRIGGER IF EXISTS update_appointments_updated_at ON appointments;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_doctors_updated_at BEFORE UPDATE ON doctors FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_prescriptions_updated_at BEFORE UPDATE ON prescriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_health_vitals_updated_at BEFORE UPDATE ON health_vitals FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_medical_reports_updated_at BEFORE UPDATE ON medical_reports FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_medical_history_updated_at BEFORE UPDATE ON medical_history FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON appointments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
