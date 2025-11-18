-- Add user_id column to patients table to link with users
ALTER TABLE patients ADD COLUMN IF NOT EXISTS user_id VARCHAR(36) REFERENCES users(user_id);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_patients_user_id ON patients(user_id);
