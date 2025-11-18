-- Update doctors table to match the full DoctorResponse model
-- Add missing columns for doctor information

-- Add new columns if they don't exist
ALTER TABLE doctors
ADD COLUMN IF NOT EXISTS sub_specializations JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS license_state VARCHAR(100),
ADD COLUMN IF NOT EXISTS qualifications JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS years_of_experience INTEGER,
ADD COLUMN IF NOT EXISTS primary_organization_id VARCHAR(36),
ADD COLUMN IF NOT EXISTS organization_affiliations JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS consultation_fee DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS availability JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS languages_spoken JSONB DEFAULT '["English"]'::jsonb,
ADD COLUMN IF NOT EXISTS rating DECIMAL(3,2) DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS total_patients_treated INTEGER DEFAULT 0;

-- Rename existing columns to match model (if they exist)
-- Note: These will fail silently if columns don't exist, which is OK
DO $$
BEGIN
  -- Rename experience_years to years_of_experience if it exists
  IF EXISTS(SELECT 1 FROM information_schema.columns
            WHERE table_name='doctors' AND column_name='experience_years') THEN
    ALTER TABLE doctors RENAME COLUMN experience_years TO years_of_experience;
  END IF;

  -- Rename education to qualifications if it exists
  IF EXISTS(SELECT 1 FROM information_schema.columns
            WHERE table_name='doctors' AND column_name='education') THEN
    ALTER TABLE doctors RENAME COLUMN education TO qualifications;
  END IF;
END $$;

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_doctors_specialization ON doctors(specialization);
CREATE INDEX IF NOT EXISTS idx_doctors_license_number ON doctors(license_number);
CREATE INDEX IF NOT EXISTS idx_doctors_is_active ON doctors(is_active);
CREATE INDEX IF NOT EXISTS idx_doctors_rating ON doctors(rating);
